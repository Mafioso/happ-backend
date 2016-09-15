from django.test import SimpleTestCase

from happ.models import Event
from happ.factories import UserFactory, CityFactory, CityInterestsFactory, EventFactory
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
