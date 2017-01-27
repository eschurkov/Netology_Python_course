import requests
import os


def read_news(news_filename):
    news = ''
    if os.path.exists(news_filename):
        with open(news_filename, encoding='utf-8') as news_file:
            # news = '\n\r'.join(list(line.strip() for line in news_file if line.strip()))
            news = news_file.read()
    return news


def detect_lang(text):
    url = 'https://translate.yandex.net/api/v1.5/tr.json/detect'
    key = 'trnsl.1.1.20161025T233221Z.47834a66fd7895d0.a95fd4bfde5c1794fa433453956bd261eae80152'

    params = {
        'key': key,
        'text': text,
    }
    return requests.get(url, params=params).json()['lang']


def translate_it(text, from_lang, to_lang):
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    key = 'trnsl.1.1.20161025T233221Z.47834a66fd7895d0.a95fd4bfde5c1794fa433453956bd261eae80152'

    if from_lang:
        lang_param = from_lang + '-' + to_lang
    else:
        lang_param = to_lang

    params = {
        'key': key,
        'lang': lang_param,
        'text': text,
    }
    response = requests.get(url, params=params).json()
    return ' '.join(response['text'])


def write_translated_file(to_filename, news_text):
    with open(to_filename, 'w', encoding='utf-8') as news_file:
        news_file.write(news_text)


source_filename = input('Путь к файлу с новостями: ').strip()
destination_filename = input('Путь к файлу с переводом: ').strip()

recommended_lang = detect_lang(read_news(source_filename))

from_language = input(
    'Язык, с которого перевести (рекомендуемый - "' + recommended_lang + '", также можете оставить пустым): ').strip()
to_language = input('Язык, на который перевести: ')

translated_text = translate_it(read_news(source_filename), from_language, to_language)
write_translated_file(destination_filename, translated_text)
