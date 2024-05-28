import pathlib
from lambo.segmenter.lambo import Lambo

input_file = pathlib.Path.home() / 'data' / 'tribble' / 'an_text.tsv'
output_file = pathlib.Path.home() / 'data' / 'tribble' / 'an_text_sentences.tsv'

lambo = Lambo.get('Spanish')
handle = open(output_file,'w')

for line in open(input_file):
    parts = line.split('\t')
    print(parts[0])
    text = parts[2].replace('\\n','\n').replace('\\t','\t')
    document = lambo.segment(text)
    for turn in document.turns:
        for sentence in turn.sentences:
            sentence_text = sentence.text.strip()
            if len(sentence_text)>20:
                handle.write(parts[0]+'\t'+parts[1]+'\t'+sentence_text.replace('\t','\\t').replace('\n','\\n')+'\n')
    #break

handle.close()
