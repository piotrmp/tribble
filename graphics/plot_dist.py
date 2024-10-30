import os
import pandas as pd
import matplotlib.pyplot as plt

directory = '../data/processed/filtered/'
dfs = []
for filename in os.listdir(directory):
    if filename.startswith("filtered_"):
        df = pd.read_csv(directory + filename)
        dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)
combined_df.to_csv('../data/processed/final/final.csv', index=False)
lang_counts = combined_df['tgt_lang'].value_counts()
plt.figure(figsize=(12, 6))
lang_counts.plot(kind='bar')
plt.title('Initial Language Distribution')
plt.xlabel('Language')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()