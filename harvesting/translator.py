import subprocess


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
        assert (len(sentences) == len(result))
    result = [r.replace('*','') for r in result]
    return result
