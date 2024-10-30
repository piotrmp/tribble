from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline
from sonar.models.blaser.loader import load_blaser_model

blaser = load_blaser_model("blaser_2_0_qe").eval()
text_embedder = TextToEmbeddingModelPipeline(encoder="text_sonar_basic_encoder", tokenizer="text_sonar_basic_encoder")


def blaser_predict(src, tgt, src_lang, tgt_lang):
    src_embs = text_embedder.predict([src], source_lang=src_lang)
    mt_embs = text_embedder.predict([tgt], source_lang=tgt_lang)
    return blaser(src=src_embs, mt=mt_embs).item()


if __name__ == "__main__":
    score = blaser_predict("Le chat s'assit sur le tapis.", "The cat sat down on the carpet.", "fra_Latn", "eng_Latn")
    print(score)
