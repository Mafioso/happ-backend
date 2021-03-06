import os
import json
import random
from bson.dbref import DBRef
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from happ.factories import UserFactory
from happ.models import Event, User


class Command(BaseCommand):
    help = 'Creates random users using UserFactory'

    def handle(self, *args, **options):
        user_refs = [DBRef(User._meta['collection'], uid) for uid in User.objects().values_list('id')]
        for evt in Event.objects(in_favourites__exists=False):
            evt.in_favourites = random.sample(user_refs, 3)
            evt.save()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created {} users'.format(options['n'])
            )
        )
