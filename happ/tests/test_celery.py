from django.test import SimpleTestCase, override_settings

from ..tasks import translate_event
from ..models import Localized
from ..factories import EventFactory
from . import *


class CeleryTests(SimpleTestCase):

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_translate_event(self):
        """
        ensure that translate_event task works properly
        """

        event = EventFactory()
        event.save()

        n = Localized.objects.count()

        self.assertTrue(translate_event.delay(id=event.id, target='de'))
        self.assertEqual(Localized.objects.count(), (n+1))
