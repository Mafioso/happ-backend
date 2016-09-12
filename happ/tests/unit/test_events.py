from django.test import SimpleTestCase

from happ.models import Upvote, Event
from happ.factories import UserFactory, EventFactory
from .. import *


class Tests(SimpleTestCase):

    def test_upvote(self):
        """
        ensure that we can upvote
        """

        u = UserFactory()
        e = EventFactory()

        count = e.votes.count()
        n = e.votes_num

        self.assertTrue(e.upvote(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.votes.count(), n+1)
        self.assertEqual(e.votes_num, n+1)

        # we cannot upvote again
        self.assertFalse(e.upvote(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.votes.count(), n+1)
        self.assertEqual(e.votes_num, n+1)

    def test_is_upvoted(self):
        """
        ensure that after upvoting is_upvoted returns True
        """

        u = UserFactory()
        e = EventFactory()
        self.assertFalse(e.is_upvoted(u))

        e.upvote(u)
        e = Event.objects.get(id=e.id)
        self.assertTrue(e.is_upvoted(u))

    def test_downvote(self):
        """
        ensure that we can downvote
        """

        u = UserFactory()
        e = EventFactory()

        count = e.votes.count()
        n = e.votes_num

        # we cannot downvote before upvote
        self.assertFalse(e.downvote(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.votes.count(), n)
        self.assertEqual(e.votes_num, n)

        e.upvote(u)
        e = Event.objects.get(id=e.id)
        self.assertTrue(e.downvote(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.votes.count(), n)
        self.assertEqual(e.votes_num, n)