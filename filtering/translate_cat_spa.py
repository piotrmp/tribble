import pandas as pd
from tqdm import tqdm
from utils.translate import translate_apertium

df = pd.read_csv('../data/processed/formatted/cat_arn.csv')

tqdm.pandas()

df['src_text'] = df['src_text'].progress_apply(lambda x: translate_apertium(x,'cat','spa'))
df['source'] = 'translated apertium cat_arn.csv'
df['src_lang'] = 'spa_Latn'
df.to_csv('../data/processed/formatted/translated_spa_arn.csv', index=False)