import os
import pandas as pd

lang_codes = {"es": "spa_Latn", "cat": "cat_Latn", "ast": "ast_Latn", "arn": "arn_Latn", "an": "arg_Latn",
              "oc": "oci_Latn"}

directory = '../data/combined'


for filename in os.listdir(directory):
    if filename.startswith("combined_") and len(filename.split("_")) == 3:
        _, lang1, lang2 = filename.split("_")
        lang2 = lang2.split(".")[0]

        df = pd.read_csv(os.path.join(directory, filename))

        df = df.rename(columns={lang1: 'src_text', lang2: 'tgt_text'})

        df['src_lang'] = lang_codes[lang1]
        df['tgt_lang'] = lang_codes[lang2]
        df = df.dropna()
        print(f"{lang1}-{lang2} length: {len(df)}")
        df.to_csv(os.path.join('../data/processed/formatted', f"{lang1}_{lang2}.{filename.split('.')[1]}"), index=False)

print("Processing complete.")
