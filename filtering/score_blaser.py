import os
import pandas as pd
from tqdm.auto import tqdm
from utils.blaser_qe import blaser_predict

lang_codes = {"es": "spa_Latn", "cat": "cat_Latn", "ast": "ast_Latn", "arn": "arn_Latn", "an": "arg_Latn",
              "oc": "oci_Latn"}

directory = '../data/combined'

tqdm.pandas(desc="scoring")

map_aranese = {"arn_Latn": "oci_Latn"}
for filename in os.listdir(directory):
    df = pd.read_csv(os.path.join(directory, filename))
    # Compute scores
    print("Predic blaser qe score")
    df['blaser'] = df.progress_apply(
        lambda row: blaser_predict(row['src_text'], row['tgt_text'], row['src_lang'], row['tgt_lang'] if else ), axis=1)

    df.to_csv(os.path.join('../data/processed/scored', f"scored_{filename.split('.')[0]}.{filename.split('.')[1]}"), index=False)

print("Processing complete.")
