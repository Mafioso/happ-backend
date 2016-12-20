import json
import requests

from django.conf import settings


def exchange(source, target, amount):
    url = settings.YAHOO_EXCHANGE_API.format(source, target)
    data = requests.get(url).json()
    try:
        rate = float(data['query']['results']['rate']['Rate'])
        return rate * amount
    except:
        return False
