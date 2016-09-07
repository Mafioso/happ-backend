from django.test import SimpleTestCase, override_settings

from ..tasks import translate_entity
from ..models import Localized
from ..factories import EventFactory
from . import *


class CeleryTests(SimpleTestCase):

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_translate_entity(self):
        """
        ensure that translate_entity task works properly
        """

        event = EventFactory()
        event.save()

        n = Localized.objects.count()

        self.assertTrue(translate_entity.delay(cls=event.__class__, id=event.id, target='de'))
        self.assertEqual(Localized.objects.count(), (n+1))
