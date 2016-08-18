import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from happ.models import Country, City


class Command(BaseCommand):
    help = 'Creates currencies from currencies.json fixtures'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'happ/fixtures/cities.json'), 'r') as f:
            s = json.loads(f.read())
            i = 0
            for k, v in s.iteritems():
                country = Country.objects.create(name=k)
                for c in v:
                    city = City.objects.create(name=c, country=country)
                i += len(v)
                self.stdout.write(
                    'Created {} cities {}'.format(len(v), self.style.SUCCESS('[ OK ]')),
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created {} counties and {} cities'.format(len(s), i)
                )
            )
