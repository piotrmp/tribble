import pandas as pd
from tqdm.auto import tqdm
import requests
import urllib.request
import pyzipper

url = "https://github.com/transducens/PILAR/raw/main/FLORES+.zip"
password = "multilingual machine translation"
zip_file = "FLORES+.zip"


def download_file(url, filename):
    urllib.request.urlretrieve(url, filename)


def extract_zip(zip_file, password):
    print("Extracting files...")
    with pyzipper.AESZipFile(zip_file, 'r') as zf:
        zf.setpassword(password.encode('utf-8'))
        zf.extractall()


def read_lang_file(lang_code, split='dev'):
    file_path = f'{split}.{lang_code}'
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def main():
    # Download the ZIP file
    download_file(url, zip_file)
    extract_zip(zip_file, password)

    lang_codes = {"spa_Latn": "es", "ast_Latn": "ast", "arn_Latn": "arn", "arg_Latn": "an"}
    data = {lang: read_lang_file(lang) for lang in lang_codes.keys()}

    df = pd.DataFrame(data)
    print(df.head())

    df.to_csv('../data/flores/flores_parallel.csv', index=False)
    print("Parallel corpus saved to 'flores.csv'")

    data = {lang_code: read_lang_file(lang) for lang, lang_code in lang_codes.items()}

    # Create and save combinations
    for lang, short_code in lang_codes.items():
        if short_code != "es":
            df = pd.DataFrame({
                "es": data["es"],
                short_code: data[short_code]
            })

            output_file = f'../data/flores/es-{short_code}_flores.csv'
            df.to_csv(output_file, index=False)
            print(f"Parallel corpus for es-{short_code} saved to '{output_file}'")
            print(df.head())
            print("\n")


if __name__ == "__main__":
    main()
