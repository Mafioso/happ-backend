from django.test import SimpleTestCase

from happ.factories import InterestFactory
from .. import *


class Tests(SimpleTestCase):

    def test_deactivate(self):
        """
        we can deactivate interest
        """
        i = InterestFactory(is_active=True)
        self.assertTrue(i.is_active)

        i.deactivate()
        self.assertFalse(i.is_active)
