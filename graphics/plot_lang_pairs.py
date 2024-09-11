import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

df = pd.read_csv('../data/processed/final/final.csv')
lang_pair_counts = pd.crosstab(df['src_lang'], df['tgt_lang'])

# Create a custom purple colormap
colors = ['#FFFFFF', '#3A0A5C', '#6B238E', '#9C3CC3', '#C565C7', '#E2A9F3']
n_bins = 100
cmap_purple = LinearSegmentedColormap.from_list('custom_purple', colors, N=n_bins)

plt.figure(figsize=(8, 6))
sns.heatmap(lang_pair_counts, annot=True, fmt='d', cmap=cmap_purple, cbar_kws={'label': 'Count'},
            annot_kws={'size': 14})

plt.title('Distribution of Source and Target Language Pairs', fontsize=16)
plt.xlabel('Target Language', fontsize=14)
plt.ylabel('Source Language', fontsize=14)

plt.xticks(rotation=45, ha='right', fontsize=14)
plt.yticks(fontsize=14)

plt.tight_layout()

plt.savefig('lang_pair_distribution.png')
plt.show()

