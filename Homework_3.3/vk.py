#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.parse import urlencode, urlparse
import requests
from time import sleep

APP_ID = 5859502
VERSION = '5.62'
auth_url = 'https://oauth.vk.com/authorize'

params = {
    'client_id': APP_ID,
    'response_type': 'token',
    'v': VERSION,
    'scope': 'friends, users'
}
# print('?'.join((auth_url, urlencode(params))))

token_url = 'https://oauth.vk.com/blank.html#access_token=67fee3842f238deaeaaf2daf56c3796f0b71a1c9f01b97426f24b262a3bcfd76e96fa1bece56d43b701af&expires_in=86400&user_id=125435'

token_parse = dict([item.split('=') for item in urlparse(token_url).fragment.split('&')])
access_token = token_parse['access_token']
params = {
    'access_token': access_token,
    'v': VERSION
}

my_friends = requests.get('https://api.vk.com/method/friends.get', params).json()['response']['items']
k = len(my_friends)
result_set = set(my_friends)
i = 0
print('Выполнение:')
for user_id in list(result_set):
    i += 1
    percent = round(i / k * 100)
    params['user_id'] = user_id
    friend_response = requests.get('https://api.vk.com/method/friends.get', params).json()
    print('%d%%' % percent)
    if 'response' in friend_response:
        result_set.intersection_update(friend_response['response']['items'])
    sleep(0.2)

params.pop('user_id')
params['user_ids'] = ','.join(list(map(str, result_set)))

friend_response = requests.get('https://api.vk.com/method/users.get', params).json()['response']
friends_names = [' '.join((item['first_name'], item['last_name'])) for item in friend_response]

print('\nОбщие друзья для всех (id):')
print(*friends_names, sep='\n')
