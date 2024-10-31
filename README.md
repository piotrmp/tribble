# TRIBBLE - TRanslating IBerian languages Based on Limited E-resources

This repository contains the code and resources for the TRIBBLE project, developed as part of the **WMT24 Shared Task on Translation into Low-Resource Languages of Spain**. Our work focuses on machine translation for three low-resource languages: **Aragonese (spa-arg)**, **Aranese (spa-arn)**, and **Asturian (spa-ast)**.

## Overview

TRIBBLE is designed to address the challenge of limited e-resources for these endangered Iberian languages by adapting a multilingual model in a constrained translation setting. We leverage the **distilled NLLB-200 model** with **600M parameters**, extending its vocabulary with two new language-specific tokens: `arn_Latn` for Aranese and `arg_Latn` for Aragonese. These tokens are initialized with weights from `oci_Latn` (Occitan) for Aranese and `spa_Latn` (Spanish) for Aragonese, reflecting linguistic similarities.

The system uses carefully processed datasets to train the model on language pairs: **Spanish to Aragonese**, **Spanish to Aranese**, and **Spanish to Asturian**. Our results are benchmarked against the **Apertium baseline**, showing comparable performance for **Asturian** and identifying challenges in **Aragonese** and **Aranese** translation quality.

### Key Results

| Language Direction       | BLEU (Apertium) | chrF (Apertium) | BLEU (TRIBBLE) | chrF (TRIBBLE) |
|--------------------------|-----------------|-----------------|----------------|----------------|
| Spanish → Aragonese      | 61.1            | 79.3            | 49.2           | 73.6           |
| Spanish → Aranese        | 28.8            | 49.4            | 23.9           | 46.1           |
| Spanish → Asturian       | 17.0            | 50.8            | **17.9**       | 50.5           |

## Repository Structure

- **data**: Contains processed datasets used in training. `final.csv` holds the final processed language pairs.
- **filtering**: Scripts for data acquisition, formatting, and filtering. Includes scripts for downloading FLORES, PILAR, OPUS, and Wikipedia data, filtering, and combining data, as well as `score_blaser.py` for quality evaluation.
- **graphics**: Scripts to generate plots for language pair distributions.
- **harvesting**: Data alignment and sentence processing tools, including scripts for sentence alignment, translation.
- **install**: Installation script for the required components.
- **requirements.txt**: Lists the dependencies needed to run the project.
- **runs**: Contains scripts for training runs, including fine-tuning and parameter adjustments.
- **scripts**: Main script for running sequence-to-sequence training.
- **utils**: Utility scripts for deduplication, language detection, length ratio calculation, normalization, and translation.

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/piotrmp/tribble.git
cd tribble
pip install -r requirements.txt
```

## Usage

1. **Data Preparation**:
   - Pre-process data using scripts in `filtering` and `harvesting`. Final pre-processed datasets should be stored in `data/processed/final/final.csv`.

2. **Model Training**:
   - Run training using the main script in `scripts/run_peft_seq2seq.py`.

3. **Evaluation**:
   - Use `score_blaser.py` in `filtering` to evaluate the translation quality with BLEU and chrF scores.

## Citation

If you use this code or refer to the TRIBBLE project, please cite the paper as follows:

```bibtex
@InProceedings{kuzmin-EtAl:2024:WMT,
  author    = {Kuzmin, Igor  and  Przybyła, Piotr  and  McGill, Euan  and  Saggion, Horacio},
  title     = {TRIBBLE - TRanslating IBerian languages Based on Limited E-resources},
  booktitle = {Proceedings of the Ninth Conference on Machine Translation},
  month     = {November},
  year      = {2024},
  address   = {Miami, Florida, USA},
  publisher = {Association for Computational Linguistics},
  pages     = {955--959},
  abstract  = {In this short overview paper, we describe our system submission for the language pairs Spanish to Aragonese (spa-arg), Spanish to Aranese (spa-arn), and Spanish to Asturian (spa-ast). We train a unified model for all language pairs in the constrained scenario. In addition, we add two language control tokens for Aragonese and Aranese Occitan, as there is already one present for Asturian. We take the distilled NLLB-200 model with 600M parameters and extend special tokens with 2 tokens that denote target languages (arn_Latn, arg_Latn) because Asturian was already presented in NLLB-200 model. We adapt the model by training on a special regime of data augmentation with both monolingual and bilingual training data for the language pairs in this challenge.},
  url       = {https://aclanthology.org/2024.wmt-1.94}
}
```
