from django.test import SimpleTestCase

from happ.models import Upvote, Event
from happ.factories import (
    UserFactory,
    EventFactory,
    UpvoteFactory,
    InterestFactory,
    ComplaintFactory,
    RejectionReasonFactory,
)
from .. import *


class Tests(SimpleTestCase):

    def test_copy(self):
        """
        we can copy event
        """
        i = InterestFactory()
        author = UserFactory()
        upvote = UpvoteFactory()
        favourited_u = UserFactory()
        e = EventFactory(
            status=random.choice(Event.STATUSES),
            author=author,
            interests=[i],
            in_favourites=[favourited_u],
            votes=[upvote],
            votes_num=1
        )
        ComplaintFactory(event=e)
        RejectionReasonFactory(event=e)

        e2 = e.copy()
        self.assertEqual(e2.status, Event.MODERATION)
        self.assertEqual(e2.author, author)
        self.assertEqual(e2.interests, [i])
        self.assertEqual(e2.in_favourites, [])
        self.assertEqual(e2.votes, [])
        self.assertEqual(e2.votes_num, 0)
        self.assertEqual(len(e2.rejection_reasons), 0)
        self.assertEqual(len(e2.complaints), 0)

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

    def test_add_to_favourites(self):
        """
        ensure that we can add to favourites
        """

        u = UserFactory()
        e = EventFactory()

        count = len(e.in_favourites)

        self.assertTrue(e.add_to_favourites(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(len(e.in_favourites), count+1)

        # we cannot add to favourites again
        self.assertFalse(e.add_to_favourites(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(len(e.in_favourites), count+1)

    def test_is_in_favourites(self):
        """
        ensure that after adding to favourites returns True
        """

        u = UserFactory()
        e = EventFactory()
        self.assertFalse(e.is_in_favourites(u))

        e.add_to_favourites(u)
        e = Event.objects.get(id=e.id)
        self.assertTrue(e.is_in_favourites(u))

    def test_remove_from_favourites(self):
        """
        ensure that we can remove from favourites
        """

        u = UserFactory()
        e = EventFactory()

        count = len(e.in_favourites)

        # we cannot remove from favourites before adding
        self.assertFalse(e.remove_from_favourites(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(len(e.in_favourites), count)

        e.add_to_favourites(u)
        e = Event.objects.get(id=e.id)
        self.assertTrue(e.remove_from_favourites(u))
        e = Event.objects.get(id=e.id)
        self.assertEqual(len(e.in_favourites), count)

    def test_approve(self):
        """
        we can approve event
        """
        e = EventFactory()
        self.assertEqual(e.status, Event.MODERATION)

        e.approve()
        self.assertEqual(e.status, Event.APPROVED)

    def test_reject(self):
        """
        we can reject event
        """
        text = "Disgusting"
        u = UserFactory()

        e = EventFactory()
        self.assertEqual(e.status, Event.MODERATION)
        self.assertEqual(len(e.rejection_reasons), 0)

        e.reject(text=text, author=u)
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.status, Event.REJECTED)
        self.assertEqual(len(e.rejection_reasons), 1)
