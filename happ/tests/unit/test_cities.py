import random
from django.test import SimpleTestCase

from happ.models import City
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

    def test_get_nearest(self):
        """
        we can get nearest city by geopoint
        """
        center = [random.uniform(-180, 180), random.uniform(-90, 90)]
        radius = 50000
        c = CityFactory(geopoint=center)

        for i in range(5):
            CityFactory(
                geopoint=generate_geopoint(center, radius),
            )

        self.assertEqual(City.get_nearest(center), c)
