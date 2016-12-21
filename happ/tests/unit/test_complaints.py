from django.test import SimpleTestCase

from happ.models import Complaint
from happ.factories import ComplaintFactory, UserFactory
from .. import *


class Tests(SimpleTestCase):

    def test_activate(self):
        """
        we can reply on complaint
        """
        u = UserFactory()
        c = ComplaintFactory()
        self.assertEqual(c.status, Complaint.OPEN)
        self.assertEqual(c.answer, None)
        self.assertEqual(c.date_answered, None)
        self.assertEqual(c.executor, None)

        c.reply(answer='Considered', executor=u)
        self.assertEqual(c.status, Complaint.CLOSED)
        self.assertEqual(c.answer, 'Considered')
        self.assertNotEqual(c.date_answered, None)
        self.assertEqual(c.executor, u)
