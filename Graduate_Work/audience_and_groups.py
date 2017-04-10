#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.parse import urlencode, urlparse, urljoin
import requests
import json
import os
import time
import datetime
import re
from collections import Counter


# функция получения токена Вконтакте
# проверяет текущий токен, если нет доступа, то предлагает пройти аутентификацию
def vk_auth():
    with open('config.json') as config:
        config_data = json.load(config)
    ip = requests.get('http://ip-api.com/json').json()['query']
    check_data = {
        'access_token': config_data['service_token'],
        'client_secret': config_data['client_secret'],
        'token': config_data['access_token'],
        'v': config_data['api_version'],
        'ip': ip
    }
    response = requests.get('https://api.vk.com/method/secure.checkToken', check_data).json()
    # print(response)
    if 'error' in response:
        auth_url = 'https://oauth.vk.com/authorize'
        auth_data = {
            'client_id': config_data['app_id'],
            'response_type': 'token',
            'v': config_data['api_version'],
            'scope': 'friends,users,groups'
        }
        get_token_url = '?'.join((auth_url, urlencode(auth_data)))
        print('Необходимо пройти авторизацию. Пройдите по ссылке - {}'.format(get_token_url))
        token_url = input('Скопируйте ссылку из адресной строки браузера:\n')
        token_parse = dict(item.split('=') for item in urlparse(token_url).fragment.split('&'))
        config_data['access_token'] = token_parse['access_token']
        with open('config.json', 'w', encoding='utf-8') as json_file:
            json.dump(config_data, json_file, ensure_ascii=False, indent=2)
    return config_data['access_token']


# функция записывает данные в файл
def get_json_file(json_data, json_filename):
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)
        print('Данные сохранены в файл "{}"'.format(json_filename))


# класс, включающий методы для работы с API (v.5.63) Вконтакте для анализа аудитории
class Vk(object):
    _VK_API_URL = 'https://api.vk.com/method/'
    _VERSION = '5.63'
    params = {
        'access_token': None,
        'v': _VERSION,
        'count': 1000,
        'offset': 0
    }

    def __init__(self, token):
        self.params['access_token'] = token

    # метод собирает id друзей и подписичков пользователя Вконтакте
    # метод API execute позволит увеличить скорость обработки в 25 раз (в теории, на практике ~ в 16 раз)
    def get_list_by_id(self, method, uid, fields=''):
        url = urljoin(self._VK_API_URL, 'execute')
        result_list = list()
        offset = 0
        script_path = os.path.join('vk_scripts', 'api_execute_get_list_by_id.js')
        with open(script_path, encoding='utf-8') as script_file:
            source_code = script_file.read()
        start_time = time.time()
        print('Собираем данные:')
        while True:
            code = source_code
            # используется re.sub вместо replace, так как source_code - не строка
            replace_dict = {'@uid@': str(uid), '@offset@': str(offset), '@method@': method, '@fields@': fields}
            for key, value in replace_dict.items():
                code = re.sub(key, value, code)
            self.params['code'] = code
            response = requests.get(url, self.params).json()
            if 'execute_errors' in response:
                print('Ошибка: {}. Данные для id={} не собраны.'.
                      format(response['execute_errors'][0]['error_msg'], uid))
            if 'response' in response:
                result_list.extend(response['response']['items'])
                passed_time = time.time() - start_time
                time_to_end = (passed_time * response['response']['total_count']) / len(result_list) - passed_time
                if len(result_list) != response['response']['total_count']:
                    print('Собрано {} из {} за {}. До конца осталось примерно {}...'.
                          format(len(result_list),
                                 response['response']['total_count'],
                                 datetime.timedelta(seconds=round(passed_time)),
                                 datetime.timedelta(seconds=round(time_to_end)))
                          )
                else:
                    print('Сбор данных ({}) завершен за {}.'.
                          format(len(result_list), datetime.timedelta(seconds=round(passed_time))))
                if len(response['response']['items']) < 25000:
                    break
                offset += 25000
            if 'error' in response:
                print('Ошибка сбора данных:', response['error']['error_msg'])
            # пауза для ограничения частоты запросов
            # при необходимости установить значение от 0.1 до 0.3
            time.sleep(0.2)
        self.params.pop('code')
        return result_list

    # метод собирает group_id групп пользователей, user_id которых переданы в параметре user_list
    def get_groups_by_ids(self, method, user_list):
        url = urljoin(self._VK_API_URL, 'execute')
        result_list = list()
        script_path = os.path.join('vk_scripts', 'api_execute_get_data_by_list.js')
        with open(script_path, encoding='utf-8') as script_file:
            source_code = script_file.read()
        users_processed = 0
        user_count = len(user_list)
        start_time = time.time()
        print('Начало обработки данных...')
        while True:
            check_list = user_list[users_processed:users_processed + 25]
            code = re.sub('@uslist@', ','.join(map(str, check_list)), source_code)
            code = re.sub('@method@', method, code)
            self.params['code'] = code
            response = requests.get(url, self.params).json()
            if 'execute_errors' in response:
                for key, error in enumerate(response['execute_errors']):
                    if error['method'] == 'groups.get':
                        print('Ошибка: {}. Данные для id={} не найдены.'.
                              format(response['execute_errors'][key]['error_msg'],
                                     response['response']['user_errors'][key])
                              )
            if 'response' in response:
                result_list.extend(response['response']['items'])
                users_processed += response['response']['users_processed']
                passed_time = time.time() - start_time
                time_to_end = (passed_time * user_count) / users_processed - passed_time
                if users_processed != user_count:
                    print('Обработано {} пользователей за {}. До конца осталось примерно {}...'.
                          format(users_processed,
                                 datetime.timedelta(seconds=round(passed_time)),
                                 datetime.timedelta(seconds=round(time_to_end)))
                          )
                else:
                    print('Обработка данных завершена. Получена информация по {} пользователям за {}.'.
                          format(users_processed, datetime.timedelta(seconds=round(passed_time)))
                          )
                    break
            if 'error' in response:
                print('Ошибка обработки:', response['error']['error_msg'])
            # пауза для ограничения частоты запросов
            # при необходимости установить значение от 0.1 до 0.3
            # time.sleep(0.3)
        self.params.pop('code')
        return result_list

    # метод возвращает информацию по списку group_id групп, переданных в параметре top_groups_list
    def get_groups_info(self, top_groups_list):
        url = urljoin(self._VK_API_URL, 'groups.getById')
        self.params['group_ids'] = ','.join(map(str, top_groups_list))
        response = requests.get(url, self.params).json()
        self.params.pop('group_ids')
        if 'error' in response:
            print('Ошибка обработки данных: {}'.format(response['error']['error_msg']))
            return False
        elif 'response' in response:
            return response['response']

    # метод возвращает топ-100 групп по численности друзей и подписчиков пользователя Вконтакте
    def get_top_followers_groups(self, user, friends=True, followers=True):
        followers_list = list()
        if friends:
            followers_list = self.get_list_by_id('friends.get', user)
        if followers:
            followers_list.extend(self.get_list_by_id('users.getFollowers', user))
        print('Всего подписчиков: {}'.format(len(followers_list)))
        all_groups = self.get_groups_by_ids('groups.get', followers_list)
        top_groups = Counter(all_groups).most_common(100)
        top_groups_ids = [gid for gid, count in top_groups]
        top_groups_info = self.get_groups_info(top_groups_ids)
        groups_list = [{'id': tgi['id'], 'title': tgi['name'], 'count': tg[1]}
                       for tgi, tg in zip(top_groups_info, top_groups)]
        return groups_list

    # метод приниает список групп и записывает данные об их участниках в файлы json
    def get_members_info(self, groups_list, data_dir='members_data'):
        for group in groups_list:
            print('Сообщество "{}":'.format(group['title']))
            members_list = self.get_list_by_id('groups.getMembers', group['id'], 'sex, bdate')
            # чистим данные. это позволит сократить объём файла (функция map работает медленнее)
            members_info_clean = [
                {'bdate': member['bdate'] if 'bdate' in member else None, 'sex': member['sex']}
                for member in members_list
                ]
            if not os.path.isdir(data_dir):
                os.mkdir(data_dir)
            file_path = os.path.join(data_dir, 'group_{}_members.json'.format(group['id']))
            get_json_file(members_info_clean, file_path)

if __name__ == "__main__":
    # получаем токен Вконтакте
    token = vk_auth()
    # запрашиваем id пользователя Вконтакте (celebrity_id = 80491907)
    while True:
        try:
            celebrity_id = int(input('Введите ID пользователя Вконтакте: '))
            break
        except ValueError:
            print('ID должен состоять из цифр')
    # запрашиваем имя для файла с результатом (не даем перезаписать конфиг)
    filename = input('Имя файла для записи JSON (top100.json): ')
    filename = filename if filename and filename != 'config.json' else 'top100.json'
    # создаем экземпляр класса и проводим сбор и запись данных (ключ followers=False отключает сбор подписчиков)
    vk_client = Vk(token)

    print('Сбор информации о группах друзей и подписичиков пользователя с id={}'.format(celebrity_id))
    top_100_groups = vk_client.get_top_followers_groups(celebrity_id, followers=True)
    get_json_file(top_100_groups, filename)

    print('Сбор информации об участниках топ-5 групп.')
    vk_client.get_members_info(top_100_groups[:5])
