import os
import urllib.request
import gzip
import shutil

def download_file(url, filename):
    urllib.request.urlretrieve(url, filename)


def unzip_file(filepath):
    with gzip.open(filepath, 'rb') as f_in:
        with open(filepath[:-3], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(filepath)

target_folder = '../data/our/'

urls = [
    'http://home.ipipan.waw.pl/p.przybyla/temp/es2an.tsv.gz',
    'http://home.ipipan.waw.pl/p.przybyla/temp/es2oc.tsv.gz',
    'http://home.ipipan.waw.pl/p.przybyla/temp/es2ast.tsv.gz'
]

for url in urls:
    filename = url.split('/')[-1]
    target_file = os.path.join(target_folder, filename)
    download_file(url, target_file)
    unzip_file(target_file)

print("All files have been downloaded and unzipped.")
