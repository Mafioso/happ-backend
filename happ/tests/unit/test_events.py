from django.test import SimpleTestCase

from happ.models import Upvote, Event
from happ.factories import UserFactory, EventFactory
from .. import *


class EventsTests(SimpleTestCase):

    def test_upvote(self):
        """
        ensure that we can upvote
        """

        u = UserFactory()
        e = EventFactory()

        count = e.votes.count()
        n = e.votes_num

        e.upvote(u)
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.votes.count(), n+1)
        self.assertEqual(e.votes_num, n+1)
