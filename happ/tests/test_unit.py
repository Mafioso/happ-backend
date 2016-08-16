import pytest
import datetime

from django.test import TestCase
from django.conf import settings

from ..models import Event
from ..factories import EventFactory


@pytest.fixture(scope="function", autouse=True)
def setup_databases(**kwargs):
    from mongoengine.connection import connect, disconnect
    disconnect()
    connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)
    print 'Creating mongo test database ' + settings.MONGODB_NAME

@pytest.fixture(scope="function", autouse=True)
def teardown_databases(**kwargs):
    from mongoengine.connection import get_connection, disconnect
    connection = get_connection()
    connection.drop_database(settings.MONGODB_NAME)
    print 'Dropping mongo test database: ' + settings.MONGODB_NAME
    disconnect()


class EventTests(TestCase):
    
    def test_event_date_field(self):
    	"""
    		ensure that we store date properly
            and we can make queries
    	"""

        for x in range(5):
            event = EventFactory(start_date=datetime.datetime(2016, 10, (x+1)))
            event.save()

        self.assertIsInstance(Event.objects.first().start_date, datetime.date)
        
        self.assertEqual(Event.objects.filter(start_date=datetime.datetime(2016, 10, 2)).count(), 1)
        self.assertEqual(Event.objects.filter(start_date__gt=datetime.datetime(2016, 10, 2)).count(), 3)
        self.assertEqual(Event.objects.filter(start_date__gte=datetime.datetime(2016, 10, 2)).count(), 4)
        self.assertEqual(Event.objects.filter(start_date__lt=datetime.datetime(2016, 10, 2)).count(), 1)
        self.assertEqual(Event.objects.filter(start_date__lte=datetime.datetime(2016, 10, 2)).count(), 2)

        self.assertEqual(Event.objects.filter(start_date=datetime.date(2016, 10, 2)).count(), 1)
        self.assertEqual(Event.objects.filter(start_date__gt=datetime.date(2016, 10, 2)).count(), 3)
        self.assertEqual(Event.objects.filter(start_date__gte=datetime.date(2016, 10, 2)).count(), 4)
        self.assertEqual(Event.objects.filter(start_date__lt=datetime.date(2016, 10, 2)).count(), 1)
        self.assertEqual(Event.objects.filter(start_date__lte=datetime.date(2016, 10, 2)).count(), 2)

    def test_event_time_field(self):
        """
            ensure that we store time properly
            and we can make queries
        """

        for x in range(5):
            event = EventFactory(start_time=datetime.datetime(2016, 10, 1, 10, (x+1), 30))
            event.save()

        self.assertIsInstance(Event.objects.first().start_time, datetime.time)
        
        self.assertEqual(Event.objects.filter(start_time=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 1)
        self.assertEqual(Event.objects.filter(start_time__gt=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 3)
        self.assertEqual(Event.objects.filter(start_time__gte=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 4)
        self.assertEqual(Event.objects.filter(start_time__lt=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 1)
        self.assertEqual(Event.objects.filter(start_time__lte=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 2)
        
        self.assertEqual(Event.objects.filter(start_time=datetime.time(10, 2, 30)).count(), 1)
        self.assertEqual(Event.objects.filter(start_time__gt=datetime.time(10, 2, 30)).count(), 3)
        self.assertEqual(Event.objects.filter(start_time__gte=datetime.time(10, 2, 30)).count(), 4)
        self.assertEqual(Event.objects.filter(start_time__lt=datetime.time(10, 2, 30)).count(), 1)
        self.assertEqual(Event.objects.filter(start_time__lte=datetime.time(10, 2, 30)).count(), 2)
