#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import csv


def get_ratings_list():
    url_rate = "http://www.cnews.ru/analytics/rating"
    response = requests.get(url_rate)
    html = response.content.decode(encoding='utf8', errors="ignore")  # читаем веб-страницу
    soup = BeautifulSoup(html, 'lxml')  # инициализируем парсер
    rating_wrapper = soup.find('div', attrs={'id': 'ratingWrapper'})
    ratings_list = rating_wrapper.find_all('ul', attrs={'class': 'dashLong'})
    rating = [
        {'name': item.text, 'link': item.get('href')}
        for ratings in ratings_list for item in ratings.find_all('a') if '2016' in item.text or '2015' in item.text
    ]
    return rating


def print_ratings_list():
    rating_list = get_ratings_list()
    print('Выберите рейтинг CNews для поиска компаний:')
    for i, rate in zip(range(len(rating_list)), rating_list):
        print('%d. %s' % (i + 1, rate['name']))
    return rating_list


def get_column_class(soup):
    td_names = ['Название компании', 'Исполнитель', 'Компания', 'Название', 'Название организации']
    for name in td_names:
        if soup.find('th', text=name):
            matches = soup.find('th', text=name)
            break
        elif soup.find('tr', attrs={'class': 'thead'}).find('td', text=name):
            matches = soup.find('tr', attrs={'class': 'thead'}).find('td', text=name)
            break
    column = matches.get('class')[0]
    return column


def get_company_list(url_full):
    if 'http://www.cnews.ru' not in url_full:
        url_full = 'http://www.cnews.ru' + url_full
    response = requests.get(url_full)
    html = response.content.decode(encoding='utf8', errors="ignore")  # читаем веб-страницу
    soup = BeautifulSoup(html, 'lxml')  # инициализируем парсер
    column = get_column_class(soup)

    matches = soup.find_all('td', attrs={'class': column})
    companies = list(map(lambda x: x.text.strip().replace('*', '').replace('(1)', '').replace('(2)', ''), matches))
    return companies


def get_vacancies(companies, keyword):

    base_url = 'https://api.hh.ru/'
    headers = {'User-Agent': 'top-it-vacancies/0.0.1 (sch.egor@gmail.com)'}

    vacancies = [['Компания', 'Вакансия', 'Зарплата', 'Описание', 'Ссылка']]
    print('Проверяем вакансии...')
    for company in companies[0:50]:
        params = {
            'text': 'NAME:' + keyword + ' AND COMPANY_NAME:' + company,
            'area': '1'
        }
        print(company, end=' - ')
        answer = requests.get(base_url + 'vacancies', headers=headers, params=params).json()['items']
        print(len(answer))
        for item in answer:
            vacancy = list()
            vacancy.append(item['employer']['name'])
            vacancy.append(item['name'])
            vacancy.append(item['salary'])
            vacancy.append(item['snippet']['responsibility'])
            vacancy.append(item['alternate_url'])
            vacancies.append(vacancy)

    csv.register_dialect('customcsv', delimiter=';', quoting=csv.QUOTE_NONE, quotechar='', escapechar='\\')
    with open("output.csv", "w", encoding='cp1251', newline='') as f:
        writer = csv.writer(f, 'customcsv')
        writer.writerows(vacancies)

rating_list = print_ratings_list()
user_select = int(input('Выберите номер: '))

companies = get_company_list(rating_list[user_select-1]['link'])
keyword = input('Ключевое слово (в названии вакансии): ').strip()

get_vacancies(companies, keyword)
