import json
import requests

from django.conf import settings

RATES = {
    'USDKZT': 311.5600,
    'KZTUSD': 0.0032,
    'EURKZT': 328.7200,
    'KZTEUR': 0.0030,
    'USDEUR': 0.9472,
    'EURUSD': 1.0551
}

def exchange_api(source, target, amount):
    url = settings.YAHOO_EXCHANGE_API.format(source, target)
    data = requests.get(url).json()
    try:
        rate = float(data['query']['results']['rate']['Rate'])
        return round(rate * amount, 2)
    except:
        return False

def exchange(source, target, amount):
    rate = float(RATES['{}{}'.format(source, target)])
    return round(rate * amount, 2)

