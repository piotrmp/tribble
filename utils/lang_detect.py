# Adapted from https://github.com/transducens/idiomata_cognitor/tree/main
import fasttext
from huggingface_hub import hf_hub_download
from typing import Union, List, Tuple
import joblib

idiomata_cognitor_labels = {
    1.: 'spa_Latn',
    2.: 'cat_Latn',
    3.: 'arg_Latn',
    4.: 'arn_Latn',
    5.: 'oci_Latn',
    6.: 'ast_Latn',
    7.: 'glg_Latn',
    8.: 'ita_Latn',
    9.: 'fra_Latn',
    10.: 'por_Latn'
}
# Load the model
idiomata_cognitor = joblib.load('../data/idiomata_cognitor/model.pkl')

def idiomata_cognitor_predict(sentence: str)->str:
    pred = idiomata_cognitor.predict([sentence])[0]
    # print(pred[0])
    return idiomata_cognitor_labels[pred], None




# Global variable to store the loaded model
_model = None


def fasttext_predict(text: Union[str, List[str]]) -> Union[Tuple[str, float], List[Tuple[str, float]]]:
    global _model

    if _model is None:
        model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
        _model = fasttext.load_model(model_path)

    def predict_single(t: str) -> Tuple[str, float]:
        labels, scores = _model.predict(t)
        return labels[0].replace('__label__', ''), float(scores[0])

    if isinstance(text, str):
        return predict_single(text)
    elif isinstance(text, list):
        return [predict_single(t) for t in text]
    else:
        raise ValueError("Input must be a string or a list of strings")