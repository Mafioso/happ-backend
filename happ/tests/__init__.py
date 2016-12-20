import pytest
import urllib
import random
from math import sin, cos, sqrt, atan2, degrees, radians

from django.conf import settings
from django.core.urlresolvers import reverse

from mongoengine.connection import connect, disconnect, get_connection


def prepare_url(path_name, query={}, *args, **kwargs):
    url = reverse(path_name, *args, **kwargs)
    url += '?' + urllib.urlencode(query)
    return url

def calc_distance(p1, p2):
    lng1 = radians(p1[0])
    lat1 = radians(p1[1])
    lng2 = radians(p2[0])
    lat2 = radians(p2[1])
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return settings.EARTH_RADIUS * c

def generate_geopoint(center, radius, inside=True):
    deg = degrees(radius / settings.EARTH_RADIUS)
    if inside:
        while True:
            lng = random.uniform(center[0]-deg, center[0]+deg)
            lat = random.uniform(center[1]-deg, center[1]+deg)
            distance = calc_distance(center, [lng, lat])

            if distance < radius:
                return [lng, lat]
    else:
        while True:
            lng = random.uniform(-180, 180)
            lat = random.uniform(-90, 90)
            distance = calc_distance(center, [lng, lat])
            if distance > radius:
                return [lng, lat]

@pytest.fixture(scope="function", autouse=True)
def setup_databases(**kwargs):
    disconnect()
    connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)

@pytest.fixture(scope="function", autouse=True)
def teardown_databases(**kwargs):
    connection = get_connection()
    connection.drop_database(settings.MONGODB_NAME)
    disconnect()
