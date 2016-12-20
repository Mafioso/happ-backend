import random

from django.test import SimpleTestCase

from happ.models import Event
from happ.factories import UserFactory, CityFactory, CityInterestsFactory, EventFactory, InterestFactory
from .. import *


class Tests(SimpleTestCase):

    def test_user_current_interests(self):
        """
        ensure that it returns interests in accordance with current city
        """

        c1 = CityFactory()
        c2 = CityFactory()

        u = UserFactory()

        self.assertEqual(len(u.current_interests), 0)

        interests1 = CityInterestsFactory(c=c1)
        interests2 = CityInterestsFactory(c=c2)

        u.settings.city = c1
        u.interests = [interests1]
        u.save()
        self.assertEqual(len(u.current_interests), len(interests1.ins))

        u.settings.city = c2
        u.interests = [interests2]
        u.save()
        self.assertEqual(len(u.current_interests), len(interests2.ins))

    def test_get_favourites(self):
        """
        we can take favourite event of current user
        """

        u = UserFactory()

        for i in range(5):
            EventFactory()

        map(lambda x: x.add_to_favourites(u), Event.objects.all()[:4])
        self.assertEqual(len(u.get_favourites()), 4)

        Event.objects.all()[0].remove_from_favourites(u)
        self.assertEqual(len(u.get_favourites()), 3)

    def test_get_feed(self):
        """
        we can take feed for a particular user
        """
        c1 = CityFactory()
        c2 = CityFactory()

        # this set is not used
        ins_set1 = map(lambda _: InterestFactory(), range(5))

        # this set is assigned to user for current city
        ins_set2 = map(lambda _: InterestFactory(), range(3))

        # this set is assigned to user but for an another city
        ins_set3 = map(lambda _: InterestFactory(), range(4))

        ci1 = CityInterestsFactory(c=c1, ins=ins_set2)
        ci2 = CityInterestsFactory(c=c2, ins=ins_set3)

        u = UserFactory()
        u.interests = [ci1, ci2]
        u.settings.city = c1
        u.save()

        for i in range(3):
            if i % 2 == 1:
                EventFactory(city=c1, interests=[random.choice(ins_set2)], type=Event.FEATURED, status=Event.APPROVED)
            else:
                EventFactory(city=c1, interests=[random.choice(ins_set2)], type=random.choice([Event.NORMAL, Event.ADS]), status=Event.APPROVED)

        for i in range(4):
            EventFactory(city=c2, interests=[random.choice(ins_set3)], status=Event.APPROVED)

        self.assertEqual(len(u.get_feed()), 2)

    def test_get_featured(self):
        """
        we can take featured events for a particular user
        """
        c1 = CityFactory()
        c2 = CityFactory()

        # this set is not used
        ins_set1 = map(lambda _: InterestFactory(), range(5))

        # this set is assigned to user for current city
        ins_set2 = map(lambda _: InterestFactory(), range(3))

        # this set is assigned to user but for an another city
        ins_set3 = map(lambda _: InterestFactory(), range(4))

        ci1 = CityInterestsFactory(c=c1, ins=ins_set2)
        ci2 = CityInterestsFactory(c=c2, ins=ins_set3)

        u = UserFactory()
        u.interests = [ci1, ci2]
        u.settings.city = c1
        u.save()

        for i in range(3):
            if i % 2 == 1:
                # this event is going to be in final set because one of the interest matches
                EventFactory(city=c1, interests=[random.choice(ins_set2), random.choice(ins_set3)], type=Event.FEATURED, status=Event.APPROVED)

                # this event will be skipped because no one interest matches user's current set
                EventFactory(city=c1, interests=[random.choice(ins_set3)], type=Event.FEATURED, status=Event.APPROVED)
            else:
                # this event is not featured
                EventFactory(city=c1, interests=[random.choice(ins_set2), random.choice(ins_set3)], type=random.choice([Event.NORMAL, Event.ADS]), status=Event.APPROVED)

        for i in range(4):
            # NORMAL events by default
            EventFactory(city=c2, interests=[random.choice(ins_set3)], status=Event.APPROVED)

        self.assertEqual(len(u.get_featured()), 1)

    def test_get_organizer_feed(self):
        """
        we can take organizer feed for a particular user
        """

        u1 = UserFactory()
        u2 = UserFactory()

        for i in range(3):
            if i % 2 == 1:
                EventFactory(author=u1)
            else:
                EventFactory(author=u2)

        self.assertEqual(len(u1.get_organizer_feed()), 1)
        self.assertEqual(len(u2.get_organizer_feed()), 2)

    def test_get_explore_feed(self):
        """
        we can take explore feed for a particular user
        """

        c = CityFactory()

        parent_interest1 = InterestFactory(parent=None)
        parent_interest2 = InterestFactory(parent=None)

        # this set is not used
        ins_set1 = map(lambda _: InterestFactory(parent=parent_interest1), range(5))

        # this set is assigned to user for current city
        ins_set2 = map(lambda _: InterestFactory(parent=parent_interest2), range(3))

        ci = CityInterestsFactory(c=c, ins=[parent_interest1])

        u = UserFactory()
        u.interests = [ci]
        u.settings.city = c
        u.save()

        for i in range(3):
            EventFactory(city=c, interests=[random.choice(ins_set1)], type=random.choice([Event.NORMAL, Event.ADS]), status=Event.APPROVED)

        for i in range(4):
            EventFactory(city=c, interests=[random.choice(ins_set2)], type=random.choice([Event.NORMAL, Event.ADS]), status=Event.APPROVED)

        self.assertEqual(len(u.get_explore()), 3)
        for e in u.get_explore():
            for i in e.interests:
                self.assertTrue(i in parent_interest1.family)
        for e in u.get_explore():
            for i in e.interests:
                self.assertFalse(i in parent_interest2.family)

    def test_get_map_feed(self):
        """
        we can take map feed for a particular user
        """
        c = CityFactory()

        ins_set = map(lambda _: InterestFactory(), range(3))
        ci = CityInterestsFactory(c=c, ins=ins_set)

        u = UserFactory()
        u.interests = [ci]
        u.settings.city = c
        u.save()

        center = [random.uniform(-180, 180), random.uniform(-90, 90)]
        radius = 50000

        for i in range(5):
            EventFactory(
                city=c,
                interests=[random.choice(ins_set)],
                type=Event.NORMAL,
                geopoint=generate_geopoint(center, radius),
            )

        for i in range(10):
            EventFactory(
                city=c,
                interests=[random.choice(ins_set)],
                type=Event.NORMAL,
                geopoint=generate_geopoint(center, radius, inside=False),
            )

        self.assertEqual(len(u.get_map_feed(center, radius)), 5)

    def test_activate(self):
        """
        we can activate user
        """
        u = UserFactory(is_active=False)
        self.assertFalse(u.is_active)

        u.activate()
        self.assertTrue(u.is_active)

    def test_deactivate(self):
        """
        we can deactivate user
        """
        u = UserFactory()
        self.assertTrue(u.is_active)

        u.deactivate()
        self.assertFalse(u.is_active)
