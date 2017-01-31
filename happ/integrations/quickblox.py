import hmac
import json
import random
import urllib
import requests
from hashlib import sha1
from datetime import datetime
from collections import OrderedDict


from django.conf import settings as djsettings

ENDPOINTS = {
    'settings': 'account_settings.json',
    'session': 'session.json',
    'signup': 'users.json',
}

def make_signature(string):
    key = djsettings.QUICKBLOX_AUTH_SECRET
    hashed = hmac.new(key, string, sha1)
    return hashed.hexdigest()

def settings():
    url = '{host}{path}'.format(host=djsettings.QUICKBLOX_API_ENDPOINT, path=ENDPOINTS['settings'])
    headers = {
        'QB-Account-Key': djsettings.QUICKBLOX_ACCOUNT_KEY,
    }
    response = requests.get(url, headers=headers)
    return json.loads(response.content)

def get_session():
    url = '{host}{path}'.format(host=djsettings.QUICKBLOX_API_ENDPOINT, path=ENDPOINTS['session'])
    data = OrderedDict({
        'application_id': djsettings.QUICKBLOX_APP_ID,
        'auth_key': djsettings.QUICKBLOX_AUTH_KEY,
        'nonce': random.randint(0, 100000),
        'timestamp': datetime.now().strftime('%s'),
    })
    string = urllib.urlencode(sorted(data.items(), key=lambda t: t[0]))
    data['signature'] = make_signature(string)
    response = requests.post(url, data=data)
    return json.loads(response.content)

def signup(login, password, facebook_id='', email='', full_name='', session_id=None):
    if session_id is None:
        session_id = get_session()['session']['token']
    url = '{host}{path}'.format(host=djsettings.QUICKBLOX_API_ENDPOINT, path=ENDPOINTS['signup'])
    data = {
        'user': {
            'login': login,
            'password': password,
            'email': email,
            'full_name': full_name,
            'facebook_id': facebook_id,
        }
    }
    headers = {
        'QB-Token': session_id,
    }
    response = requests.post(url, json=data, headers=headers)
    return json.loads(response.content)
