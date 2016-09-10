import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from happ.factories import UserFactory
from happ.models import User


class Command(BaseCommand):
    help = 'Creates random users using UserFactory'

    def add_arguments(self, parser):
        parser.add_argument('n', type=int)

    def handle(self, *args, **options):
        users = [UserFactory.build() for x in xrange(options['n'])]
        User.objects.insert(users)
        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created {} users'.format(options['n'])
                )
            )
