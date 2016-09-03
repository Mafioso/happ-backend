import json
import requests

from django.conf import settings


def translate(string, target):
    url = settings.GOOGLE_TRANSLATE_LINK.format(settings.GOOGLE_TRANSLATE_KEY, string, target)
    response = requests.get(url)
    return json.loads(response.content)
