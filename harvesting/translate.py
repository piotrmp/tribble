import pathlib,gzip
import subprocess

# echo "Me gusta bailar." | apertium spa-arg
# Me fa goyo bailar.
# echo "Me gusta bailar." | apertium spa-ast
# Gústame baillar.
# echo "Me gusta bailar." | apertium spa-cat | apertium ca-oc_aran
# M'agrade barar.

# echo "Me fa goyo bailar." | apertium arg-spa
# echo "Gústame baillar." | apertium ast-spa -> no existe
# echo "M'agrade barar." | apertium oc_aran-ca | apertium cat-spa

BATCH_SIZE = 128
source = 'es'
destination = 'an'
source_sentence_path = pathlib.Path.home() / 'data'/'tribble'/'segmented'/(source+'_text_sentences.tsv.gz')
destination_sentence_path = pathlib.Path.home() / 'data'/'tribble'/'translated'/(source+'_translated_'+destination+'.tsv')

def translate(sentences, src, dst):
    if src == 'es' and dst == 'an':
        model = 'spa-arg'
    elif src == 'es' and dst == 'ast':
        model = 'spa-ast'
    elif src == 'es' and dst == 'oc':
        return translate(translate(sentences, 'es', 'ca'), 'ca', 'oc')
    elif src == 'es' and dst == 'ca':
        model = 'spa-cat'
    elif src == 'ca' and dst == 'oc':
        model = 'ca-oc_aran'
    else:
        assert (False)
    sentences = [s.replace('\n', ' ').replace('\t', ' ') for s in sentences]
    try:
        joint = '\n'.join(sentences)
        process = subprocess.run(["apertium", model], stdout=subprocess.PIPE, text=True, input=joint)
        assert (process.returncode == 0)
        result = process.stdout.split('\n')
        assert (len(sentences) == len(result))
    except:
        print("Something went wrong with batch translation, trying one by one...")
        result = []
        for s in sentences:
            process = subprocess.run(["apertium", model], stdout=subprocess.PIPE, text=True, input=s)
            assert (process.returncode == 0)
            result.append(process.stdout)
    result = [r.replace('*','') for r in result]
    return result

batch = []
with open(destination_sentence_path,'w') as output:
    with gzip.open(source_sentence_path) as input:
        for i,line in enumerate(input):
            if i % 1000 == 0:
                print(str(i/1000)+'k /7,302k')
                #if i==2000:
                #    break
            line = line.decode('utf-8').rstrip()
            text = line.split('\t')[2].replace('\\n','\n').replace('\\t','\t')
            batch.append(text)
            if len(batch)==BATCH_SIZE:
                translated = translate(batch,source,destination)
                for t in translated:
                    output.write(t.replace('\n','\\n')+'\n')
                batch = []
    if len(batch)!=0:
        translated = translate(batch, source, destination)
        for t in translated:
            output.write(t.replace('\n', '\\n') + '\n')
