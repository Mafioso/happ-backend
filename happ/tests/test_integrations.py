from django.test import SimpleTestCase

from ..integrations import google
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
