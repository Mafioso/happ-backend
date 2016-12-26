from datetime import datetime
from django.test import SimpleTestCase

from happ.utils import daterange
from . import *


class Tests(SimpleTestCase):

    def test_daterange(self):
        """
        ensure that daterange integration works properly
        """

        dt1 = datetime(2016, 10, 20)
        dt2 = datetime(2016, 10, 21)
        days = [d for d in daterange(dt1, dt2)]
        self.assertEqual(len(days), 2)

        dt1 = datetime(2016, 12, 20)
        dt2 = datetime(2017, 1, 3)
        days = [d for d in daterange(dt1, dt2)]
        self.assertEqual(len(days), 15)
