import os
import json
import inspect

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import happ.migrations as happ_migrations


class Command(BaseCommand):
    help = 'Creates random users using UserFactory'

    def add_arguments(self, parser):
        parser.add_argument('n', type=str)

    def handle(self, *args, **options):
        migration_num = options['n']
        for (fn_name, fn) in inspect.getmembers(happ_migrations, inspect.isfunction):
            if fn_name.endswith(migration_num):
                fn()
                return
        self.stdout.write(
            self.style.ERROR('Probably such migration script does not exist or you forgot to add migration number at the end of the script name'))
