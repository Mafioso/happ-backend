from django.test import SimpleTestCase

from ..integrations import google, yahoo
from . import *


class Tests(SimpleTestCase):

    def test_google_translate(self):
        """
        ensure that google translate integration works properly
        """

        string = "Hello world"

        r = google.translate(string=string, target='de')
        self.assertIn('data', r)
        self.assertIn('translations', r['data'])

    def test_google_url_shortener(self):
        """
        ensure that google url shortener integration works properly
        """

        url = "http://some.domain.com/very/long/url?with=parameteres"

        r = google.url_shortener(url=url)
        self.assertIn('id', r)

    def test_google_places(self):
        """
        ensure that google places integration works properly
        """

        text = "Restaurants in Almaty"

        r = google.places(text=text)
        self.assertIn('results', r)
        self.assertEqual(r['status'], 'OK')

    def test_yahoo_exchange(self):
        """
        ensure that yahoo exchange integration works properly
        """

        amount = 100
        source = "USD"
        target = "KZT"

        r = yahoo.exchange(source=source, target=target, amount=amount)
        self.assertTrue(r)
        self.assertTrue(isinstance(r, float))

        amount = 100
        source = "USD"
        target = "NONE" # something that does not exist
        r = yahoo.exchange(source=source, target=target, amount=amount)
        self.assertFalse(r)
