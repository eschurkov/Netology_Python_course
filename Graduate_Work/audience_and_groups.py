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
def save_json_file(json_data, json_filename):
    try:
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=2)
            print('Данные сохранены в файл "{}"'.format(json_filename))
    except FileNotFoundError:
        print('Ошибка записи в файл "{}"'.format(json_filename))


# класс, включающий методы для работы с API (v.5.63) Вконтакте для анализа аудитории
class Vk:
    _VK_API_URL = 'https://api.vk.com/method/'
    _VERSION = '5.63'
    token = None

    def __init__(self, access_token):
        self.token = access_token

    def call_api(self, method, params):
        params = dict(params)
        params.update({
            'access_token': self.token,
            'v': self._VERSION,
        })
        url = urljoin(self._VK_API_URL, method)
        while True:
            r = requests.get(url, params).json()
            if 'error' in r:
                if r['error']['error_code'] == 6:
                    time.sleep(0.5)
                    print("Превышение количества запросов. Пауза 0.5 сек... Повтор запроса.")
                else:
                    raise Exception('Ошибка API: {}'.format(r['error']['error_msg']))
            else:
                return r

    def call_api_batch(self, api_commands):
        method_calls = []
        for method, params in api_commands:
            method_calls.append(
                "API.{method}({params})".format(
                    method=method,
                    params=json.dumps(params)
                )
            )
        code = 'return [' + ','.join(method_calls) + '];'
        r = self.call_api('execute', {
            'code': code
        })
        return r

    def get_data(self, api_commands, total, ftype='id'):
        time_start = time.time()
        data_list = []
        for k in range(0, len(api_commands), 25):
            now_commands = api_commands[k:k + 25]
            results = self.call_api_batch(now_commands)
            iter_errors = iter(results['execute_errors']) if 'execute_errors' in results else None
            for result, (method, params) in zip(results['response'], now_commands):
                if result:
                    data_list.extend(result['items'])
                elif iter_errors:
                    print('Ошибка сбора данных для пользователя id={}: {}'.
                          format(params['user_id'], next(iter_errors)['error_msg']))
            data_processed = len(data_list) if ftype == 'id' else k + len(now_commands)
            self.print_log(time_start, total, data_processed)
        return data_list

    @staticmethod
    def print_log(start, total, processed):
        passed_time = time.time() - start
        time_to_end = (passed_time * total) / processed - passed_time
        if total != processed:
            print('Обработано {} пользователей из {} за {}. До конца осталось примерно {}...'.
                  format(processed, total,
                         datetime.timedelta(seconds=round(passed_time)),
                         datetime.timedelta(seconds=round(time_to_end)))
                  )
        else:
            print('Обработка данных завершена. Получена информация по {} пользователям за {}.'.
                  format(processed, datetime.timedelta(seconds=round(passed_time)))
                  )

    def get_users(self, celebrity):
        return_list = []
        for method in ['friends.get', 'users.getFollowers']:
            total_count = self.call_api(
                method, {'user_id': celebrity}
            )['response']['count']
            commands = [
                (method, {'user_id': celebrity, 'count': 1000, 'offset': offset})
                for offset in range(0, total_count, 1000)]
            return_list.extend(self.get_data(commands, total_count))
        return return_list

    def get_top_groups(self, ids_list):
        commands = [('groups.get', {'user_id': user}) for user in ids_list]
        total_count = len(commands)
        gr_list = self.get_data(commands, total_count, ftype='list')

        top_groups = Counter(gr_list).most_common(100)
        top_groups_ids = [gid for gid, count in top_groups]

        top_groups_info = self.call_api(
            'groups.getById', {'group_ids': ','.join(map(str, top_groups_ids))}
        )
        return_list = [
            {'id': tgi['id'], 'title': tgi['name'], 'count': tg[1]}
            for tgi, tg in zip(top_groups_info['response'], top_groups)]
        return return_list

    def get_group_members(self, group_data):
        total_count = self.call_api('groups.getMembers', {'group_id': group_data['id']})['response']['count']
        commands = [('groups.getMembers', {
            'group_id': group_data['id'], 'fields': 'sex, bdate', 'count': 1000, 'offset': offset
        }) for offset in range(0, total_count, 1000)]
        members_data = vk_client.get_data(commands, total_count)
        # чистим данные. это позволит сократить объём файла (функция map работает медленнее)
        return_data = [
            {
                'bdate': member['bdate'] if 'bdate' in member else None,
                'sex': member['sex']
            }
            for member in members_data]
        return return_data

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
    groups_file = input('Имя файла для записи топ-100 групп (top100.json): ')
    groups_file = groups_file if groups_file and groups_file != 'config.json' else 'top100.json'

    # создаем экземпляр класса и проводим сбор и запись данных (ключ followers=False отключает сбор подписчиков)
    vk_client = Vk(token)

    print('\nСобираем друзей и подписчиков пользователя:')
    users_list = vk_client.get_users(celebrity_id)
    print('Всего собрано пользователей: {}'.format(len(users_list)))

    print('\nСобираем список групп найденных пользователей:')
    groups_list = vk_client.get_top_groups(users_list)
    save_json_file(groups_list, groups_file)

    for group in groups_list[:5]:
        print('\nСобираем данные пользователей для группы "{}":'.format(group['title']))
        members_data_clean = vk_client.get_group_members(group)
        file_path = os.path.join('members_data', 'group_{}_members.json'.format(group['id']))
        save_json_file(members_data_clean, file_path)
