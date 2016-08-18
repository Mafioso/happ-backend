import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from happ.models import Currency


class Command(BaseCommand):
    help = 'Creates currencies from currencies.json fixtures'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'happ/fixtures/currencies.json'), 'r') as f:
            s = json.loads(f.read())
            for currency in s:
                c = Currency.objects.create(name=currency)
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created {} currencies'.format(len(s))
                )
            )
