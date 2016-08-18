import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from happ.factories import InterestFactory


class Command(BaseCommand):
    help = 'Creates random interests using InterestFactory'

    def add_arguments(self, parser):
        parser.add_argument('n', type=int)

    def handle(self, *args, **options):
        for x in range(options['n']):
            interest = InterestFactory()
            interest.save()
        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created {} interests'.format(options['n'])
                )
            )
