import os
import pandas as pd
from tqdm.auto import tqdm
from utils.length_ratio import compute_length, compute_ratio, compute_unique_ratio, filter_length
from utils.lang_detect import idiomata_cognitor_predict, fasttext_predict
from utils.normalization import normalize
from utils.dedup import dedup_filter

directory = '../data/processed/formatted'

tqdm.pandas()

for filename in os.listdir(directory):
    # if 'cat_arn' in filename or 'csv' not in filename or 'oc' not in filename:
    #     continue
    tqdm.write(filename)
    df = pd.read_csv(os.path.join(directory, filename), encoding='utf-8', sep=',')

    # Normalize
    df['src_text'] = df['src_text'].progress_apply(lambda x: normalize(x))
    df['tgt_text'] = df['tgt_text'].progress_apply(lambda x: normalize(x))

    # Compute length stats
    df['src_len'] = df['src_text'].progress_apply(lambda x: compute_length(x, 1.0))
    df['tgt_len'] = df['tgt_text'].progress_apply(lambda x: compute_length(x, 1.0))
    df['len_ratio'] = df.progress_apply(lambda row: compute_ratio(row['src_len'], row['tgt_len']), axis=1)
    df['unique_ratio'] = df['src_text'].progress_apply(lambda x: compute_unique_ratio(str(x), 1.0))

    # Compute lang detect
    df['src_ic'] = df['src_text'].progress_apply(lambda x: idiomata_cognitor_predict(x)[0])
    df['tgt_ic'] = df['tgt_text'].progress_apply(lambda x: idiomata_cognitor_predict(x)[0])
    df['src_ft'] = df['src_text'].progress_apply(lambda x: fasttext_predict(x)[0])
    df['tgt_ft'] = df['tgt_text'].progress_apply(lambda x: fasttext_predict(x)[0])
    df = pd.read_csv('../data/processed/stats/stats_es_oc.csv', encoding='utf-8', sep=',')
    df = df.dropna()

    tqdm.write("\nSAVING STATISTICS ABOUT FULL")
    df.to_csv(os.path.join('../data/processed/stats', f"stats_{filename.split('.')[0]}.csv"), index=False)

    tqdm.write("\nBEGIN FILTERING")
    tqdm.write(f"{filename} length before length filtering: {len(df)}")
    df = df[df.progress_apply(lambda row: filter_length(
        row['src_len'],
        row['tgt_len'],
        row['len_ratio'],
        row['unique_ratio'],
        min_len=5,
        max_len=1050,
        max_len_ratio=9.0,
        min_src_unique_ratio=0.125
    ), axis=1)]
    tqdm.write(f"{filename} length after length filtering: {len(df)}")

    tqdm.write("\nDedup")
    df, dedup_counts = dedup_filter(
        df,
        dedup_pairs=True,
        max_source_dedup=2,  # Assume translated data
        max_target_dedup=3
    )

    tqdm.write("deduplication counts:")
    for key, value in dedup_counts.items():
        tqdm.write(f"{key}: {value}")
    tqdm.write(f"{filename} length after dedup filtering: {len(df)}")

    # Filter by distance score
    tqdm.write("FILTER BY DISTANCE SCORE")
    df = df[(df['score'] >= 0.6) & (df['score'] <= 1.0)]
    tqdm.write(f"{filename} length after score filtering: {len(df)}")

    # Filter by Lang IDs
    tqdm.write("FILTER ALL ENGLISH TEXT")
    df = df[(df['src_ft'] != 'eng_Latn') | (df['tgt_ft'] != 'eng_Latn')]
    tqdm.write(f"{filename} length after language filtering English: {len(df)}")

    tqdm.write("FILTER NOT MATCHING SRC AND TGT PAIRS TEXTS")
    if 'oc' in filename.split('.')[0]:
        print("CUSTOM")
        ## Evaluate Occitan because Aranese is sub group
        df = df[df['tgt_ic'].isin(['arn_Latn', 'ast_Latn', 'arg_Latn'])]
        df['tgt_lang'] = df['tgt_ic']
        df = df[~((~df['source'].str.contains('flores')) &
                  (~df['source'].str.contains('pilar')) &
                  ((df['src_ic'] != df['src_lang']) |
                   (df['tgt_ic'] != df['tgt_lang'])))]
    else:
        df = df[~((~df['source'].str.contains('flores')) &
                  (~df['source'].str.contains('pilar')) &
                  ((df['src_ic'] != df['src_lang']) |
                   (df['tgt_ic'] != df['tgt_lang'])))]

    tqdm.write(f"{filename} length after language filtering: {len(df)}")

    df.to_csv(os.path.join('../data/processed/filtered', f"filtered_{filename.split('.')[0]}.csv"), index=False)
    tqdm.write(f"{filename} finished")

tqdm.write("Processing complete.")
