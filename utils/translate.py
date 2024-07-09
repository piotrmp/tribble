import requests


def translate_apertium(text, src_lang='cat', tgt_lang='spa'):
    url = "https://www.apertium.org/apy/translate"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "langpair": f"{src_lang}|{tgt_lang}",
        "q": text,
        "markUnknown": "no"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        result = response.json()
        translated_text = result['responseData']['translatedText']
        return translated_text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


# src_lang = "cat"  # Catalan
# tgt_lang = "spa"  # Spanish
# text_to_translate = "Concèpte e classificacion."
# translated = translate_apertium(text_to_translate, src_lang, tgt_lang)
# if translated:
#     print(f"Original: {text_to_translate}")
#     print(f"Translated: {translated}")
