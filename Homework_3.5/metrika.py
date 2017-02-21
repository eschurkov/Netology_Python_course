import json
from urllib.parse import urlencode, urlparse, urljoin
from pprint import pprint
import requests

AUTHORIZE_URL = 'https://oauth.yandex.ru/authorize'
APP_ID = 'ef228d8a94db439588a3e449683abe0e'  # Your app_id here

auth_data = {
    'response_type': 'token',
    'client_id': APP_ID
}
print('?'.join((AUTHORIZE_URL, urlencode(auth_data))))

TOKEN = 'AQAAAAANnsA_AAQOZICLvf2aj0QhoyyFhpqvaWk'  # Your token here


class YandexMetrika(object):
    _METRIKA_STAT_URL = 'https://api-metrika.yandex.ru/stat/v1/'
    _METRIKA_MANAGEMENT_URL = 'https://api-metrika.yandex.ru/management/v1/'
    token = None

    def get_header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token),
            'User-Agent': 'Google Chrome 56.0.2924 (WebKit 537.36)'
        }

    @property
    def counter_list(self):
        url = urljoin(self._METRIKA_MANAGEMENT_URL, 'counters')
        headers = self.get_header()
        response = requests.get(url, headers=headers)
        counter_list = [c['id'] for c in response.json()['counters']]
        return counter_list


class YMReports(YandexMetrika):
    def __init__(self, token):
        self.token = token

    def get_visits_count(self, counter_id):
        url = urljoin(self._METRIKA_STAT_URL, 'data')
        headers = self.get_header()
        params = {
            'id': counter_id,
            'metrics': 'ym:s:visits'
        }
        response = requests.get(url, params, headers=headers)
        # pprint(response.json())
        visits_count = response.json()['data'][0]['metrics'][0]
        return visits_count

    def get_pageviews_count(self, counter_id):
        url = urljoin(self._METRIKA_STAT_URL, 'data')
        headers = self.get_header()
        params = {
            'id': counter_id,
            'metrics': 'ym:s:pageviews'
        }
        response = requests.get(url, params, headers=headers)
        # pprint(response.json())
        pageviews_count = response.json()['data'][0]['metrics'][0]
        return pageviews_count

    def get_users_count(self, counter_id):
        url = urljoin(self._METRIKA_STAT_URL, 'data')
        headers = self.get_header()
        params = {
            'id': counter_id,
            'metrics': 'ym:s:users'
        }
        response = requests.get(url, params, headers=headers)
        # pprint(response.json())
        users_count = response.json()['data'][0]['metrics'][0]
        return users_count


class YMControl(YandexMetrika):
    def __init__(self, token):
        self.token = token

    def change_counter_name(self, counter_id, counter_name):
        url = urljoin(self._METRIKA_MANAGEMENT_URL, 'counter/%d' % counter_id)
        headers = self.get_header()
        data = {
            'counter': {
                'name': counter_name
            }
        }
        response = requests.put(url, json.dumps(data), headers=headers)
        # pprint(response.json())
        new_name = response.json()['counter']['name']
        return new_name

metrika_reports = YMReports(TOKEN)
metrika_control = YMControl(TOKEN)

for counter in metrika_reports.counter_list:
    print('Информация по счетчику %d' % counter)
    print('Суммарное количество визитов: %d' % metrika_reports.get_visits_count(counter))
    print('Число просмотров страниц на сайте за отчетный период: %d' % metrika_reports.get_pageviews_count(counter))
    print('Количество уникальных посетителей: %d' % metrika_reports.get_users_count(counter))

counter = int(input('Номер счетчика для переименования ({}): '.format(','.join(map(str, metrika_control.counter_list)))))
new_name = input('Новое название счетчика:')
try:
    print('Переименовано в "%s".' % metrika_control.change_counter_name(counter, new_name))
except KeyError:
    print('Ошибка')
