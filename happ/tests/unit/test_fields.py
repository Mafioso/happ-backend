import datetime

from django.test import SimpleTestCase

from happ.models import EventTime
from happ.factories import EventTimeFactory
from .. import *


class Tests(SimpleTestCase):

    def test_event_date_field(self):
        """
            ensure that we store date properly
            and we can make queries
        """

        for x in range(5):
            event = EventTimeFactory(date=datetime.datetime(2016, 10, (x+1)))
            event.save()

        self.assertIsInstance(EventTime.objects.first().date, datetime.date)

        self.assertEqual(EventTime.objects.filter(date=datetime.datetime(2016, 10, 2)).count(), 1)
        self.assertEqual(EventTime.objects.filter(date__gt=datetime.datetime(2016, 10, 2)).count(), 3)
        self.assertEqual(EventTime.objects.filter(date__gte=datetime.datetime(2016, 10, 2)).count(), 4)
        self.assertEqual(EventTime.objects.filter(date__lt=datetime.datetime(2016, 10, 2)).count(), 1)
        self.assertEqual(EventTime.objects.filter(date__lte=datetime.datetime(2016, 10, 2)).count(), 2)

        self.assertEqual(EventTime.objects.filter(date=datetime.date(2016, 10, 2)).count(), 1)
        self.assertEqual(EventTime.objects.filter(date__gt=datetime.date(2016, 10, 2)).count(), 3)
        self.assertEqual(EventTime.objects.filter(date__gte=datetime.date(2016, 10, 2)).count(), 4)
        self.assertEqual(EventTime.objects.filter(date__lt=datetime.date(2016, 10, 2)).count(), 1)
        self.assertEqual(EventTime.objects.filter(date__lte=datetime.date(2016, 10, 2)).count(), 2)

    def test_event_time_field(self):
        """
            ensure that we store time properly
            and we can make queries
        """

        EventTime.objects.delete()
        for x in range(5):
            event = EventTimeFactory(start_time=datetime.datetime(2016, 10, 1, 10, (x+1), 30))
            event.save()

        self.assertIsInstance(EventTime.objects.first().start_time, datetime.time)

        self.assertEqual(EventTime.objects.filter(start_time=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 1)
        self.assertEqual(EventTime.objects.filter(start_time__gt=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 3)
        self.assertEqual(EventTime.objects.filter(start_time__gte=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 4)
        self.assertEqual(EventTime.objects.filter(start_time__lt=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 1)
        self.assertEqual(EventTime.objects.filter(start_time__lte=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 2)

        self.assertEqual(EventTime.objects.filter(start_time=datetime.time(10, 2, 30)).count(), 1)
        self.assertEqual(EventTime.objects.filter(start_time__gt=datetime.time(10, 2, 30)).count(), 3)
        self.assertEqual(EventTime.objects.filter(start_time__gte=datetime.time(10, 2, 30)).count(), 4)
        self.assertEqual(EventTime.objects.filter(start_time__lt=datetime.time(10, 2, 30)).count(), 1)
        self.assertEqual(EventTime.objects.filter(start_time__lte=datetime.time(10, 2, 30)).count(), 2)
