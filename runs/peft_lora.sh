python scripts/run_peft_seq2seq.py \
    --model_name_or_path igorktech/nllb-pruned-6L-512d-finetuned-spa-40k \
    --use_peft True \
    --lora_r 16 \
    --lora_alpha 32 \
    --dataset_name your_dataset_name \
    --no_cuda True \
    --output_dir ./results \
    --evaluation_strategy steps \
    --eval_steps 250 \
    --save_strategy steps \
    --save_steps 250 \
    --logging_steps 10 \
    --learning_rate 5e-4 \
    --weight_decay 1e-3 \
    --optim adamw_torch \
    --lr_scheduler_type constant_with_warmup \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 16 \
    --weight_decay 1e-3 \
    --save_total_limit 3 \
    --num_train_epochs 1 \
    --predict_with_generate True \
    --fp16 False \
    --push_to_hub True \
    --hub_model_id igorktech/model \
    --report_to wandb