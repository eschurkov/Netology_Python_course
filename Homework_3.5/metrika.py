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

    def __init__(self, token):
        self.token = token

    def get_header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token),
            'User-Agent': 'asdasdasd'
        }

    @property
    def counter_list(self):
        url = urljoin(self._METRIKA_MANAGEMENT_URL, 'counters')
        headers = self.get_header()
        response = requests.get(url, headers=headers)
        counter_list = [c['id'] for c in response.json()['counters']]
        return counter_list

    def get_visits_count(self, counter_id):
        url = urljoin(self._METRIKA_STAT_URL, 'data')
        headers = self.get_header()
        params = {
            'id': counter_id,
            'metrics': 'ym:s:visits'
        }
        response = requests.get(url, params, headers=headers)
        pprint(response.json())
        visits_count = response.json()['data'][0]['metrics'][0]
        return visits_count


metrika = YandexMetrika(TOKEN)
print(YandexMetrika.__dict__)
print(metrika.__dict__)

print(metrika.counter_list)

for counter in metrika.counter_list:
    print(metrika.get_visits_count(counter))
