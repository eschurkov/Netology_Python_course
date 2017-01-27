import json
import codecs
import re
from collections import Counter

files = [
    {'name': 'newsfr.json', 'encoding': 'iso8859_5'},
    {'name': 'newscy.json', 'encoding': 'koi8-r'},
    # {'name': 'newsit.json', 'encoding': 'cp1251'},
    {'name': 'newsafr.json', 'encoding': 'utf-8'}
]

def read_file(file):
    with codecs.open(file['name'], encoding=file['encoding']) as news_file:
        return json.load(news_file)


def count_words(news):
    words = Counter()
    # пока не знаю, как сделать так, чтобы и ссылки не попадали  перечень слов и все слэши '/' убрать
    clean_trash = re.compile('\W+ ?')
    for k in range(len(news['rss']['channel']['item'])):
        words += Counter(
            # чистим строку от лишних знкаков, <br>
            clean_trash.sub(' ',
                            news['rss']['channel']['item'][k]['description']['__cdata'].replace('<br>', '')).split()
        )
    # фильтруем слова с длиной больше 6 букв  оставляем 10 первых
    big_words = list(filter(lambda x: len(x[0]) > 6, words.most_common()))[:10]
    return big_words

def print_words(filename, words):
    print('\nПервая десятка слов больше 6 символов в текстах новостей файла', filename)
    for word in words:
        print('{0} - {1}'.format(word[0], word[1]))

for file in files:
    # news = read_file(file)
    # big_words = count_words(news)
    print_words(file['name'], count_words(read_file(file)))
