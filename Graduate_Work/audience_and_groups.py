#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.parse import urlencode, urlparse, urljoin
import requests
from time import sleep
import json
import os
import time
import re
from pprint import pprint


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


def get_json_file(json_data, json_filename='top100.json'):
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)


class Vk(object):
    _VK_API_URL = 'https://api.vk.com/method/'
    _VERSION = '5.63'
    params = {
        'access_token': None,
        'v': _VERSION,
        'user_id': None,
        'count': 1000,
        'offset': 0,
        'extended': 1
    }

    def __init__(self, token):
        self.params['access_token'] = token

    def get_list(self, method, uid):
        url = urljoin(self._VK_API_URL, method)
        self.params['group_id'] = uid
        self.params['user_id'] = uid
        self.params['offset'] = 0
        result_list = list()
        while True:
            response = requests.get(url, self.params).json()
            if 'error' in response:
                print('Ошибка: {}. Данные для id={} не собраны.'.
                      format(response['error']['error_msg'], uid))
            else:
                response = response['response']['items']
                result_list.extend(response)
            # к методам API ВКонтакте можно обращаться не чаще 3 раз в секунду
            sleep(0.3)
            # если длина ответа меньше 1000, то дальше данных нет
            if len(response) < 1000:
                break
            print(self.params['offset'])
            self.params['offset'] += 1000

        return result_list

    @staticmethod
    def groups_dict_construct(list_data, groups):
        for group in list_data:
            if group['id'] in groups:
                groups[group['id']]['count'] += 1
            else:
                ag = {
                    group['id']: {'title': group['name'], 'count': 1}
                }
                groups.update(ag)
        return groups

    def get_top_followers_groups(self, user, friends=True, followers=True):
        followers_list = list()
        if friends:
            followers_list = self.get_list('friends.get', user)
        if followers:
            followers_list.extend(self.get_list('users.getFollowers', user))
        groups = dict()
        print('Всего подписчиков: {}'.format(len(followers_list)))
        i = 0
        for user_id in followers_list:
            i += 1
            print('Обрабатываем пользователя №{} (id={}). Осталось {} подпичисков.'.
                  format(i, user_id, len(followers_list) - i))
            self.groups_dict_construct(self.get_list('groups.get', user_id), groups)
        groups_list = sorted(list(groups.values()), key=lambda x: x['count'], reverse=True)[:100]
        return groups_list

    # метод execute позволит увеличить скорость обработки в 25 раз (в теории, на практике ~ в 16 раз)
    def get_list_by_id(self, method, uid):
        url = urljoin(self._VK_API_URL, 'execute')
        result_list = list()
        offset = 0
        script_path = os.path.join('vk_scripts', 'api_execute_get_list_by_id.js')
        with open(script_path, encoding='utf-8') as script_file:
            source_code = script_file.read()
        while True:
            code = re.sub('@uid@', str(uid), source_code)
            code = re.sub('@offset@', str(offset), code)
            code = re.sub('@method@', method, code)
            self.params['code'] = code
            response = requests.get(url, self.params).json()
            if 'execute_errors' in response:
                print('Ошибка: {}. Данные для id={} не собраны.'.
                      format(response['execute_errors'][0]['error_msg'], uid))
            else:
                response = response['response']['items']
                result_list.extend(response)
            if len(response) < 25000:
                break
            # к методам API ВКонтакте можно обращаться не чаще 3 раз в секунду
            sleep(0.3)
            print(offset)
            offset += 25000
        return result_list

    def get_groups_by_list(self, user_list):
        user_list = [125435, 207270, 3528564, 1405118, 1405188]  # debug
        url = urljoin(self._VK_API_URL, 'execute')
        result_list = list()
        script_path = os.path.join('vk_scripts', 'api_execute_get_groups_by_list.js')
        with open(script_path, encoding='utf-8') as script_file:
            source_code = script_file.read()
        users_processed = 0
        while users_processed < len(user_list):
            check_list = user_list[users_processed:users_processed + 25]
            code = re.sub('@uslist@', ','.join(map(str, check_list)), source_code)
            self.params['code'] = code
            response = requests.get(url, self.params).json()
            if 'execute_errors' in response:
                for key, error in enumerate(response['execute_errors']):
                    if error['method'] == 'groups.get':
                        print('Ошибка: {}. Данные для id={} не собраны.'.
                              format(response['execute_errors'][key]['error_msg'],
                                     response['response']['user_errors'][key])
                              )
            if 'response' in response:
                result_list.extend(response['response']['items'])
            users_processed += response['response']['users_processed']
        return result_list


if __name__ == "__main__":
    token = vk_auth()

    while True:
        try:
            celebrity_id = int(input('Введите ID пользователя Вконтакте: '))
            break
        except ValueError:
            print('ID должен состоять из цифр')
    # celebrity_id = 80491907

    filename = input('Имя файла для записи JSON (top_groups.json): ')
    filename = filename if filename and filename != 'config.json' else 'top100.json'

    vk_client = Vk(token)
    print('start execute', time.time())
    get_json_file(vk_client.get_top_followers_groups(celebrity_id, followers=False), json_filename=filename)
    print('end execute1', time.time())
