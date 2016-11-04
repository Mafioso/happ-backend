from django.test import SimpleTestCase

from happ.factories import CityFactory
from .. import *


class Tests(SimpleTestCase):

    def test_activate(self):
        """
        we can activate city
        """
        c = CityFactory(is_active=False)
        self.assertFalse(c.is_active)

        c.activate()
        self.assertTrue(c.is_active)

    def test_deactivate(self):
        """
        we can deactivate city
        """
        c = CityFactory(is_active=True)
        self.assertTrue(c.is_active)

        c.deactivate()
        self.assertFalse(c.is_active)
