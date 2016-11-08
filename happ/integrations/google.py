import json
import requests

from django.conf import settings


def translate(string, target):
    url = settings.GOOGLE_TRANSLATE_LINK.format(settings.GOOGLE_API_KEY, string, target)
    response = requests.get(url)
    return json.loads(response.content)

def url_shortener(url):
    url = settings.GOOGLE_URL_SHORTENER_LINK.format(settings.GOOGLE_API_KEY)
    payload = {
        "longUrl": url
    }
    response = requests.post(url, json=payload)
    return json.loads(response.content)
