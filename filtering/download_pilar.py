import urllib.request
import zipfile
import pandas as pd

def download_file(url, filename):
    urllib.request.urlretrieve(url, filename)

def unzip_file(zipname, password=None):
    with zipfile.ZipFile(zipname, 'r') as zip_ref:
        if password:
            zip_ref.extractall(pwd=password.encode())
        else:
            zip_ref.extractall()

def main():
    # Download files
    download_file("https://github.com/transducens/PILAR/raw/main/aranese/sentences.aranese_catalan.filtered.aranese.zip", "sentences.aranese_catalan.filtered.aranese.zip")
    download_file("https://github.com/transducens/PILAR/raw/main/aranese/sentences.aranese_catalan.filtered.catalan.zip", "sentences.aranese_catalan.filtered.catalan.zip")

    unzip_file("sentences.aranese_catalan.filtered.aranese.zip")
    unzip_file("sentences.aranese_catalan.filtered.catalan.zip")

    with open('sentences.aranese_catalan.aranese.txt', 'r', encoding='utf-8') as f:
        aranese_sentences = f.read().splitlines()
    with open('sentences.aranese_catalan.catalan.txt', 'r', encoding='utf-8') as f:
        catalan_sentences = f.read().splitlines()

    df = pd.DataFrame({
        'arn': aranese_sentences,
        'cat': catalan_sentences
    })

    df.to_csv('../data/pilar/cat-arn_pilar.csv', index=False)

if __name__ == '__main__':
    main()