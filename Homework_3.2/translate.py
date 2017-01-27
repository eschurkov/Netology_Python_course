import requests
import os
import glob


def read_news(news_filename):
    news = ''
    if os.path.exists(news_filename):
        with open(news_filename, encoding='utf-8') as news_file:
            news = news_file.read()
    return news


def find_files(source_directory):
    files_path = os.path.join(source_directory, '*.txt')
    return glob.glob(files_path)


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
    if not (os.path.exists(os.path.dirname(to_filename))):
        os.mkdir(os.path.dirname(to_filename))
    with open(to_filename, 'w', encoding='utf-8') as news_file:
        news_file.write(news_text)


def translate_file(source_filename, destination_filename, from_language, to_language):
    translated_text = translate_it(read_news(source_filename), from_language, to_language)
    write_translated_file(destination_filename, translated_text)


def translate_one_file():
    source_filename = input('Путь к файлу с новостями: ').strip()
    destination_filename = input('Путь к файлу с переводом: ').strip()

    recommended_lang = detect_lang(read_news(source_filename))

    from_language = input(
        'Язык, с которого перевести (рекомендуемый - "' + recommended_lang + '", также можете оставить пустым): ')
    to_language = input('Язык, на который перевести: ')

    translate_file(source_filename, destination_filename, from_language, to_language)


def translate_directory():
    source_directory = input('Путь к папке с файлами новостей: ').strip()
    destination_directory = input('Путь к папке с результатом перевода: ').strip()
    from_language = ''
    to_language = input('Язык, на который перевести: ')

    source_files = find_files(source_directory)
    for source_filename in source_files:
        new_name = os.path.basename(source_filename).split('.')[0] + '-' + to_language + '.txt'
        destination_filename = os.path.join(destination_directory, new_name)
        translate_file(source_filename, destination_filename, from_language, to_language)


functions = {'1': translate_one_file, '2': translate_directory}

while True:
    user_input = input(
        'Выберите действие:\n'
        '1 - Перевести один файл с новостями.\n2 - Перевести все файлы с новостями в папке.'
        '\nДля выхода введите любой другой символ.\n=> ')
    functions.get(user_input, exit)()
