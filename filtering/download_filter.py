import editdistance
import requests
import json
from opustools import OpusRead
import csv
import pathlib

from harvesting.translator import translate

out_path = pathlib.Path.home() / 'data' / 'tribble' / 'filtered'


def get_available_corpora(source, target):
    url = f"https://opus.nlpl.eu/opusapi/?source={source}&target={target}&preprocessing=raw&version=latest"
    response = requests.get(url)
    data = response.json()
    print(data)
    for corpus in data['corpora']:
        if corpus['corpus'] == 'Ubuntu':
            print(corpus)
    filtered_corpora = [
        corpus['corpus'] for corpus in data['corpora']
        if (corpus['source'] == source and corpus['target'] == target) or (
                    corpus['source'] == target and corpus['target'] == source) and corpus['source_tokens'] and corpus[
               'target_tokens']
    ]
    return filtered_corpora


def is_ok(src_line, trg_line, src_translated_line):
    text1 = src_translated_line.replace(' ', '')
    text2 = trg_line.strip().replace(' ', '')
    if len(text1) == 0 or len(text2) == 0:
        return (False,0.0)
    lev_score = 1.0 - editdistance.eval(text1, text2) / max(len(text1), len(text2))
    if lev_score > 0.8:
        return (True,lev_score)
    else:
        return (False,lev_score)


def create_parallel_tsv(directory, source, target, output_file):
    # Initialize OpusRead
    opus_reader = OpusRead(
        directory=directory,
        source=source,
        target=target,
        preprocess='xml',
        write_mode='moses',
        write=[f'{source}-{target}.src', f'{source}-{target}.trg'],
        download_dir=str(out_path / 'res'),
        suppress_prompts=True,
        verbose=True
    )
    
    # Process and write the data
    opus_reader.printPairs()
    
    # Translate the source data
    print("Translating for alignment...")
    to_translate = []
    with open(f'{source}-{target}.src', 'r', encoding='utf-8') as src_file:
        for src_line in src_file:
            to_translate.append(src_line.strip())
    src_translated = translate(to_translate, source, target)
    
    # Combine the source and target files into a single TSV
    ok_lines = 0
    nok_lines = 0
    with open(f'{source}-{target}.src', 'r', encoding='utf-8') as src_file, \
            open(f'{source}-{target}.trg', 'r', encoding='utf-8') as trg_file, \
            open(output_file, 'w', encoding='utf-8', newline='') as tsv_file:
        
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        tsv_writer.writerow([source, target])  # Write header
        
        for src_line, trg_line, src_translated_line in zip(src_file, trg_file, src_translated):
            check = is_ok(src_line, trg_line, src_translated_line)
            tsv_writer.writerow([src_line.strip(), trg_line.strip(), str(check[1])])
            if check[0]:
                ok_lines+=1
            else:
                nok_lines+=1
    
    print("OK lines: "+str(ok_lines)+" out of "+str(ok_lines+nok_lines))
    print(f"Parallel TSV file '{output_file}' has been created.")


source_lang = 'es'
for target_lang in ['an','oc','ast']:
    print("TARGET: " + target_lang)
    available_corpora = get_available_corpora(source_lang, target_lang)
    print(available_corpora)
    
    for corpus in available_corpora:
        print("CORPUS: "+corpus)
        file_path = out_path / (source_lang + '-' + target_lang + '_'+corpus+'_filtered.tsv')
        create_parallel_tsv(corpus, source_lang, target_lang, str(file_path))
