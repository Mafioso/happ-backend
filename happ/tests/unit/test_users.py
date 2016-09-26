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
            EventFactory(city=c1, interests=[random.choice(ins_set2)])

        for i in range(4):
            EventFactory(city=c2, interests=[random.choice(ins_set3)])

        self.assertEqual(len(u.get_feed()), 3)
