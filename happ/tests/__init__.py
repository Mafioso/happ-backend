import pytest

from django.conf import settings

from mongoengine.connection import connect, disconnect, get_connection


@pytest.fixture(scope="function", autouse=True)
def setup_databases(**kwargs):
    disconnect()
    connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)

@pytest.fixture(scope="function", autouse=True)
def teardown_databases(**kwargs):
    connection = get_connection()
    connection.drop_database(settings.MONGODB_NAME)
    disconnect()
