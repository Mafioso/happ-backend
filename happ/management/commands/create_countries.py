import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from happ.models import Country, Currency


class Command(BaseCommand):
    help = 'Creates countries and relevant currencies from countries.json fixtures'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'happ/fixtures/countries.json'), 'r') as f:
            s = json.loads(f.read())
            for item in s:
                currency = Currency.objects.create(name=item['currency'], code=item['code'])
                country = Country.objects.create(name=item['country'], currency=currency)

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created {} counties and {} currencies'.format(len(s), len(s))
                )
            )
