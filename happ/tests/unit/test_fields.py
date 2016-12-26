import datetime
import factory


from django.test import SimpleTestCase
from mongoengine import Document

from mongoextensions.fields import DateStringField, TimeStringField
from .. import *


class Doc(Document):
    date = DateStringField()
    time = TimeStringField()


class DocFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Doc


class Tests(SimpleTestCase):

    def test_event_date_field(self):
        """
            ensure that we store date properly
            and we can make queries
        """

        for x in range(5):
            event = DocFactory(date=datetime.datetime(2016, 10, (x+1)))
            event.save()

        self.assertIsInstance(Doc.objects.first().date, datetime.date)

        self.assertEqual(Doc.objects.filter(date=datetime.datetime(2016, 10, 2)).count(), 1)
        self.assertEqual(Doc.objects.filter(date__gt=datetime.datetime(2016, 10, 2)).count(), 3)
        self.assertEqual(Doc.objects.filter(date__gte=datetime.datetime(2016, 10, 2)).count(), 4)
        self.assertEqual(Doc.objects.filter(date__lt=datetime.datetime(2016, 10, 2)).count(), 1)
        self.assertEqual(Doc.objects.filter(date__lte=datetime.datetime(2016, 10, 2)).count(), 2)

        self.assertEqual(Doc.objects.filter(date=datetime.date(2016, 10, 2)).count(), 1)
        self.assertEqual(Doc.objects.filter(date__gt=datetime.date(2016, 10, 2)).count(), 3)
        self.assertEqual(Doc.objects.filter(date__gte=datetime.date(2016, 10, 2)).count(), 4)
        self.assertEqual(Doc.objects.filter(date__lt=datetime.date(2016, 10, 2)).count(), 1)
        self.assertEqual(Doc.objects.filter(date__lte=datetime.date(2016, 10, 2)).count(), 2)

    def test_event_time_field(self):
        """
            ensure that we store time properly
            and we can make queries
        """

        Doc.objects.delete()
        for x in range(5):
            event = DocFactory(time=datetime.datetime(2016, 10, 1, 10, (x+1), 30))
            event.save()

        self.assertIsInstance(Doc.objects.first().time, datetime.time)

        self.assertEqual(Doc.objects.filter(time=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 1)
        self.assertEqual(Doc.objects.filter(time__gt=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 3)
        self.assertEqual(Doc.objects.filter(time__gte=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 4)
        self.assertEqual(Doc.objects.filter(time__lt=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 1)
        self.assertEqual(Doc.objects.filter(time__lte=datetime.datetime(2016, 10, 1, 10, 2, 30)).count(), 2)

        self.assertEqual(Doc.objects.filter(time=datetime.time(10, 2, 30)).count(), 1)
        self.assertEqual(Doc.objects.filter(time__gt=datetime.time(10, 2, 30)).count(), 3)
        self.assertEqual(Doc.objects.filter(time__gte=datetime.time(10, 2, 30)).count(), 4)
        self.assertEqual(Doc.objects.filter(time__lt=datetime.time(10, 2, 30)).count(), 1)
        self.assertEqual(Doc.objects.filter(time__lte=datetime.time(10, 2, 30)).count(), 2)
