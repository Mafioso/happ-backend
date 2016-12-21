# -*- coding: utf-8 -*-
import os
import re
import json
import getpass
import pymysql
import datetime
import dateutil

from django.core.management.base import BaseCommand, CommandError

from progressbar import ProgressBar, SimpleProgress
from mongoengine.fields import EmailField, URLField

from happ.models import (
    User,
    UserSettings,
    Country,
    City,
    Interest,
    Event,
    FileObject,
)

# +----------------+
# | Tables_in_happ |
# +----------------+
# | + accounts     |
# | + cities       |
# | + events       |
# | + favorites    |
# | + interests    |
# | + pictures     |
# +----------------+



class Command(BaseCommand):
    help = 'Updates entities from mysql database'

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, nargs='?')
        parser.add_argument('--user', type=str, nargs='?')
        parser.add_argument('--db', type=str, nargs='?')

    def handle(self, *args, **options):
        host = options['host'] or 'localhost'
        user = options['user'] or 'root'
        db = options['db'] or 'happ'
        password = getpass.getpass('Enter password for user %s: ' % user)
        try:
            connection = pymysql.connect(host=host,
                                         user=user,
                                         password=password,
                                         db=db,
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)

            # users
            with connection.cursor() as cursor:
                roles = {
                    1: User.REGULAR,
                    10: User.MODERATOR,
                    20: User.ADMINISTRATOR,
                }
                sql = "SELECT * FROM `accounts`"
                cursor.execute(sql)
                results = cursor.fetchall()
                k = 0
                self.stdout.write(
                    self.style.WARNING(
                        'Started updating users'
                    )
                )
                pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(results)).start()
                for idx, r in enumerate(results):
                    try:
                        i = User.objects.get(username=r['email'])
                        i.password = 'sha1$$%s' % r['password']
                        i.save()
                        k+=1
                    except Exception as e:
                        pass
                    pbar.update(idx + 1)
                pbar.finish()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully updated {} users'.format(k)
                    )
                )


            connection.close()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    'Error: ' + str(e)
                )
            )
            return
