from datasets import load_dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
    HfArgumentParser,
)
from peft import get_peft_model, LoraConfig, TaskType
import wandb
import evaluate
import sacrebleu
import numpy as np
import pandas as pd
from tqdm import tqdm
import os
from codecarbon import EmissionsTracker
from dataclasses import dataclass, field
from typing import Optional, List
import random
import torch
from transformers import set_seed
from transformers.optimization import Adafactor
from transformers import get_constant_schedule_with_warmup
import logging

logging.getLogger('apscheduler.executors.default').propagate = False

@dataclass
class ModelConfig:
    model_name_or_path: str = field(default="facebook/nllb-200-distilled-600M")
    use_peft: bool = field(default=True)
    lora_r: int = field(default=16)
    lora_alpha: int = field(default=32)
    lora_dropout: float = field(default=0.05)
    lora_task_type: TaskType = field(default=TaskType.SEQ_2_SEQ_LM)
    lora_target_modules: Optional[List[str]] =field(default_factory=lambda: ['k_proj','v_proj','q_proj', 'out_proj'])
    lora_modules_to_save: Optional[List[str]] = field(default=None)

@dataclass
class DataArguments:
    dataset_name: Optional[str] = field(default=None)
    wandb_project: Optional[str] = field(default="nllb-finetuning")

def get_peft_config(model_config: ModelConfig):
    return LoraConfig(
        r=model_config.lora_r,
        lora_alpha=model_config.lora_alpha,
        lora_dropout=model_config.lora_dropout,
        bias="none",
        task_type=model_config.lora_task_type,
        target_modules="all-linear",
        # target_modules=model_config.lora_target_modules,
        modules_to_save=model_config.lora_modules_to_save,
    )
def translate(model, tokenizer, text, src_lang, tgt_lang, a=32, b=3, max_input_length=1024, num_beams=4, **kwargs):
    tokenizer.src_lang = src_lang
    tokenizer.tgt_lang = tgt_lang
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_input_length)
    result = model.generate(
        **inputs.to(model.device),
        forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang],
        max_new_tokens=int(a + b * inputs.input_ids.shape[1]),
        num_beams=num_beams,
        **kwargs
    )
    return tokenizer.batch_decode(result, skip_special_tokens=True)
def tokenize_function(example, tokenizer, model_args):
    src_lang = example["src_lang"]
    tgt_lang = example["tgt_lang"]

    tokenizer.src_lang = src_lang
    model_inputs = tokenizer(example["src_text"], max_length=256, truncation=True, padding="max_length")

    tokenizer.src_lang = tgt_lang
    labels = tokenizer(example["tgt_text"], max_length=256, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    model_inputs["src_lang"] = src_lang
    model_inputs["tgt_lang"] = tgt_lang
    return model_inputs

def compute_metrics(eval_preds, tokenizer):
    bleu_calc = sacrebleu.metrics.BLEU()
    chrf_calc = sacrebleu.metrics.CHRF(word_order=2)

    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    bleu_score = bleu_calc.corpus_score(decoded_preds, [decoded_labels])
    chrf_score = chrf_calc.corpus_score(decoded_preds, [decoded_labels])

    return {
        "bleu": bleu_score.score,
        "chrf++": chrf_score.score
    }

def main():
    parser = HfArgumentParser((ModelConfig, DataArguments, Seq2SeqTrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    set_seed(training_args.seed)

    os.makedirs("./emissions", exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_args.model_name_or_path)
    print(model)
    if model_args.use_peft:
        peft_config = get_peft_config(model_args)
        model = get_peft_model(model, peft_config)

    model.print_trainable_parameters()

    if torch.backends.mps.is_built():
        device = torch.device("mps")
    # device = torch.device('cpu')
        model = model.to(device)

    # dataset = load_dataset("wmt16", "ro-en")
    dataset = load_dataset('csv', data_files={'train': "data/processed/final/final.csv"})
    split_datasets = dataset['train'].train_test_split(test_size=0.05, seed=42)
    test_valid = split_datasets['test'].train_test_split(test_size=0.5, seed=42)

    dataset = DatasetDict({
        'train': split_datasets['train'],
        'validation': test_valid['train'],
        'test': test_valid['test']
    })
    print(f"Train set size: {len(dataset['train'])}")
    print(f"Validation set size: {len(dataset['validation'])}")
    print(f"Test set size: {len(dataset['test'])}")

    test_df = pd.DataFrame(dataset['test'])

    tokenized_datasets = dataset.map(
        lambda example: tokenize_function(example, tokenizer, model_args),
        batched=False,
        remove_columns=dataset["train"].column_names,
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    optimizer = Adafactor(
        [p for p in model.parameters() if p.requires_grad],
        scale_parameter=False,
        relative_step=False,
        lr=5e-5,
        clip_threshold=1.0,
        weight_decay=1e-3,
    )

    num_train_steps = (len(tokenized_datasets["train"]) // training_args.per_device_train_batch_size) * training_args.num_train_epochs
    warmup_steps = int(0.1 * num_train_steps)
    scheduler = get_constant_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps)

    wandb.init(project=data_args.wandb_project, config=vars(training_args))
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=lambda eval_preds: compute_metrics(eval_preds, tokenizer),
        optimizers=(optimizer, scheduler),
    )

    tracker = EmissionsTracker(project_name=data_args.wandb_project, output_dir="./emissions")
    tracker.start()

    trainer.train()


    # Identify actual language pairs in the dataset
    lang_pairs = test_df[['src_lang', 'tgt_lang']].drop_duplicates().values.tolist()

    bleu_calc = sacrebleu.metrics.BLEU()
    chrf_calc = sacrebleu.metrics.CHRF(word_order=2)

    for src_lang, tgt_lang in lang_pairs:
        print(f"Evaluating {src_lang} to {tgt_lang}")

        # Filter the test set for this language pair
        pair_df = test_df[(test_df['src_lang'] == src_lang) & (test_df['tgt_lang'] == tgt_lang)]

        # Translate
        translated = [
            translate(model, tokenizer, t, src_lang, tgt_lang)[0]
            for t in tqdm(pair_df['src_text'])
        ]

        # Compute BLEU and CHRF++
        bleu_score = bleu_calc.corpus_score(translated, [pair_df['tgt_text'].tolist()])
        chrf_score = chrf_calc.corpus_score(translated, [pair_df['tgt_text'].tolist()])

        print(f"BLEU score for {src_lang} to {tgt_lang}: {bleu_score.score}")
        print(f"CHRF++ score for {src_lang} to {tgt_lang}: {chrf_score.score}")

        # Log to wandb
        wandb.log({
            f"test_bleu_{src_lang}_{tgt_lang}": bleu_score.score,
            f"test_chrf++_{src_lang}_{tgt_lang}": chrf_score.score
        })

    emissions = tracker.stop()
    print(f"Emissions: {emissions} kg CO2eq")
    wandb.log({"emissions_kg_CO2eq": emissions})

    if training_args.push_to_hub:
        trainer.push_to_hub(**{
            "finetuned_from": model_args.model_name_or_path,
            "tasks": "translation",
            "dataset": data_args.dataset_name,
            "tags": ["peft", "lora"],
        })

    wandb.finish()

if __name__ == "__main__":
    main()