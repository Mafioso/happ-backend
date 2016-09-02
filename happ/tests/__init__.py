import pytest
import urllib

from django.conf import settings
from django.core.urlresolvers import reverse

from mongoengine.connection import connect, disconnect, get_connection


def prepare_url(path_name, query={}, *args, **kwargs):
        url = reverse(path_name, *args, **kwargs)
        url += '?' + urllib.urlencode(query)
        return url

@pytest.fixture(scope="function", autouse=True)
def setup_databases(**kwargs):
    disconnect()
    connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)

@pytest.fixture(scope="function", autouse=True)
def teardown_databases(**kwargs):
    connection = get_connection()
    connection.drop_database(settings.MONGODB_NAME)
    disconnect()
