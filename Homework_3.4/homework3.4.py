#!/usr/bin/python
# -*- coding: utf-8 -*-

import osa
from math import ceil


def get_average_temperature(filename):
    with open(filename, encoding='utf-8', errors='ignore') as tempsfile:
        f_temps = [int(line.strip().split()[0]) for line in tempsfile]
    # По условию все температуры по Фаренгейту, поэтому сначала считаем среднее, потом один раз конвертируем
    average_f_temperature = sum(f_temps) / len(f_temps)

    url = 'http://www.webservicex.net/ConvertTemperature.asmx?WSDL'
    client = osa.Client(url)
    params = {
        'Temperature': average_f_temperature,
        'FromUnit': 'degreeFahrenheit',
        'ToUnit': 'degreeCelsius'
    }
    average_c_temperature = client.service.ConvertTemp(**params)
    print('Средняя температура по Цельсию: %.2f C' % average_c_temperature)


def get_travel_costs(filename):
    with open(filename, encoding='utf-8', errors='ignore') as currencyfile:
        costs = [dict(zip(['amount', 'fromCurrency'], line.split(':')[1].split())) for line in currencyfile]
    url = 'http://fx.currencysystem.com/webservices/CurrencyServer4.asmx?WSDL'
    client = osa.Client(url)
    params = {
        'toCurrency': 'RUB',
        'rounding': True
    }
    cost_in_rub = 0
    for item in costs:
        params.update(item)
        cost_in_rub += client.service.ConvertToNum(**params)
    print('Стоимость всх билетов: %d рублей' % ceil(cost_in_rub))


def get_distance(filename):
    with open(filename, encoding='utf-8', errors='ignore') as distancefile:
        distances = [float(line.split(':')[1].replace(',', '').split()[0]) for line in distancefile]
    # По условию все расстояния в милях, поэтому сначала суммируем, потом один раз конвертируем
    distance = sum(distances)
    url = 'http://www.webservicex.net/length.asmx?WSDL'
    client = osa.Client(url)
    params = {
        'LengthValue': distance,
        'fromLengthUnit': 'Miles',
        'toLengthUnit': 'Kilometers'
    }
    distance_in_km = client.service.ChangeLengthUnit(**params)
    print('Общее расстояние - %.2f км' % distance_in_km)

get_average_temperature('data/temps.txt')
get_travel_costs('data/currencies.txt')
get_distance('data/travel.txt')
