import pathlib, editdistance, gzip
import re

_RE_COMBINE_WHITESPACE = re.compile(r"\s+")

source = 'es'
destination = 'an'

destination_sentence_path = pathlib.Path.home() / 'data' / 'tribble' / 'segmented' / (
        destination + '_text_sentences.tsv.gz')
source_sentence_path = pathlib.Path.home() / 'data' / 'tribble' / 'segmented' / (source + '_text_sentences.tsv.gz')
source_translated_sentence_path = pathlib.Path.home() / 'data' / 'tribble' / 'translated' / (
        source + '_translated_' + destination + '.tsv.gz')

output_path = pathlib.Path.home() / 'data' / 'tribble' / 'parallel' / (source + '2' + destination + '.tsv')

sentences_source = ['abc', '123', 'abc123']
sentences_destination = ['abac', '1223', 'abcabc123']


def normalise_for_lev(string):
    return _RE_COMBINE_WHITESPACE.sub(" ", string.replace('\n', ' ').replace('\t', ' ')).strip()


def align_sentences_greedy(sentences1, sentences2, originals1, originals2):
    results = []
    for sentence1, original1 in zip(sentences1, originals1):
        for sentence2, original2 in zip(sentences2, originals2):
            normalised1 = normalise_for_lev(sentence1)
            normalised2 = normalise_for_lev(sentence2)
            if len(normalised1) == 0 and len(normalised2) == 0:
                continue
            lev_score = 1.0 - editdistance.eval(normalised1, normalised2) / max(len(normalised1), len(normalised2))
            if lev_score > 0.9:
                xyz = (normalise_for_lev(original1), normalise_for_lev(original2), lev_score)
                # print(xyz)
                results.append(xyz)
    return results


destination_dict = {}
with gzip.open(destination_sentence_path) as input:
    for line in input:
        line = line.decode('utf-8').rstrip()
        article = line.split('\t')[1]
        text = line.split('\t')[2].replace('\\n', '\n').replace('\\t', '\t')
        if article in destination_dict:
            destination_dict[article].append(text)
        else:
            destination_dict[article] = [text]

previous_article = ''
counter = 0
seen = set()
print("Articles: " + str(len(destination_dict)))
with open(output_path, 'w') as output:
    with gzip.open(source_sentence_path) as source_sentences:
        with gzip.open(source_translated_sentence_path) as source_translated_sentences:
            for line, line_t in zip(source_sentences, source_translated_sentences):
                line = line.decode('utf-8').rstrip()
                article = line.split('\t')[0]
                source_text = line.split('\t')[2].replace('\\n', '\n').replace('\\t', '\t')
                translated_text = line_t.decode('utf-8').rstrip().replace('\\n', '\n').replace('\\t', '\t')
                if article in destination_dict:
                    if article != previous_article:
                        print(str(counter) + '/' + str(len(destination_dict)) + ' : ' + article)
                        counter += 1
                        previous_article = article
                    alignment = align_sentences_greedy([translated_text], destination_dict[article], [source_text],
                                                       destination_dict[article])
                    for src, dst, score in alignment:
                        if src == dst or (src, dst) in seen:
                            #print("Skipping")
                            continue
                        output.write(src + '\t' + dst + '\t' + str(score) + '\n')
                        seen.add((src, dst))

print("DONE")
