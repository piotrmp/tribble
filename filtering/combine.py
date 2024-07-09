import os
import pandas as pd
import fnmatch


def read_and_combine_files(input_folders, output_folder, lang):
    dfs = []

    for folder in input_folders:
        print(f"\nSearching in {folder}:")
        for root, dirs, files in os.walk(folder):
            for file in files:
                if fnmatch.fnmatch(file.lower(), f'*es*{lang}*.*sv'):
                    file_path = os.path.join(root, file)
                    print(f"  Reading file: {file_path}")

                    if file.endswith('.csv'):
                        df = pd.read_csv(file_path)
                        df['score'] = 1
                    elif file.endswith('.tsv'):
                        df = pd.read_csv(file_path, sep='\t',names=['es', lang, 'score'], header=0)
                        print(df.columns)
                    else:
                        print(f"Unsupported file type: {file}")
                        continue

                    df['source'] = file
                    dfs.append(df)

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        print(combined_df.tail())
        os.makedirs(output_folder, exist_ok=True)

        output_file = os.path.join(output_folder, f'combined_es_{lang}.csv')
        combined_df.to_csv(output_file, index=False)
        print(f"Combined data saved to: {output_file}")

        return combined_df
    else:
        print(f"No matching files found for language: {lang}")
        return None


input_folders = ['../data/flores/', '../data/opus/']
output_folder = '../data/processed/combined/'

# an Aragonese
# ast Asturian
# oc Occitan
# arn Aranese

for lang in ['ast', 'an', 'oc', 'arn']:
    print(f"\nProcessing language: {lang}")
    combined_data = read_and_combine_files(input_folders, output_folder, lang)

    if combined_data is not None:
        print(combined_data.head())
    print("-" * 50)