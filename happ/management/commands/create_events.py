import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from happ.factories import EventFactory
from happ.models import Event


class Command(BaseCommand):
    help = 'Creates random events using EventFactory'

    def add_arguments(self, parser):
        parser.add_argument('n', type=int)

    def handle(self, *args, **options):
        events = [EventFactory.build() for x in xrange(options['n'])]
        Event.objects.insert(events)
        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created {} events'.format(options['n'])
                )
            )
