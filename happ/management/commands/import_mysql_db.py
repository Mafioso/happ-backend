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
    help = 'Imports entities from mysql database'

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

            # interests
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `interests`"
                cursor.execute(sql)
                results = cursor.fetchall()
                self.stdout.write(
                    self.style.WARNING(
                        'Started importing interests'
                    )
                )
                pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(results)).start()
                for idx, r in enumerate(results):
                    i = Interest(
                        title=r['name'],
                        is_global=True,
                        is_active=True,
                    )
                    i.save()
                    FileObject.objects.create(path=r['picb'], entity=i)
                    pbar.update(idx + 1)
                pbar.finish()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully imported {} interests'.format(len(results))
                    )
                )

            # cities
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `cities`"
                cursor.execute(sql)
                results = cursor.fetchall()
                country = Country.objects.create(name=u'Казахстан')
                self.stdout.write(
                    self.style.WARNING(
                        'Started importing cities'
                    )
                )
                pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(results)).start()
                for idx, r in enumerate(results):
                    i = City(
                        name=r['name'],
                        geopoint=(float(r['long']), float(r['latt']), ),
                        country=country,
                        is_active=True,
                    )
                    i.save()
                    pbar.update(idx + 1)
                pbar.finish()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully imported {} cities'.format(len(results))
                    )
                )

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
                        'Started importing users'
                    )
                )
                pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(results)).start()
                for idx, r in enumerate(results):
                    try:
                        # email
                        email = None
                        if EmailField.EMAIL_REGEX.match(r['email']):
                            email = r['email']

                        i = User(
                            username=r['email'],
                            email=email,
                            gender=0 if r['sex']=='male' else 1,
                            role=roles[r['role']],
                            date_of_birth=datetime.datetime(datetime.datetime.now().year-int(r['age']), 1, 1),
                            is_active=True,
                            settings=UserSettings(),
                            date_created=r['registered'] if r['registered'] else datetime.datetime.now(),
                        )
                        i.save()
                        k+=1
                    except Exception as e:
                        pass
                    pbar.update(idx + 1)
                pbar.finish()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully imported {} users'.format(k)
                    )
                )

            # events
            with connection.cursor() as cursor:
                statuses = {
                    'active': Event.APPROVED,
                    'disabled': Event.REJECTED,
                }
                sql = "SELECT * FROM `events`"
                cursor.execute(sql)
                results = cursor.fetchall()
                self.stdout.write(
                    self.style.WARNING(
                        'Started importing events'
                    )
                )
                pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(results)).start()
                for idx, r in enumerate(results):
                    # get city
                    with connection.cursor() as cursor_1:
                        city = None
                        sql_1 = "SELECT * FROM `cities` WHERE `id`=%s"
                        cursor_1.execute(sql_1, (r['city_id']))
                        r_1 = cursor_1.fetchone()
                        if not r_1:
                            print 'City !!!!', r['name'], r['city_id']
                        else:
                            city = City.objects.get(name=r_1['name'])

                    # get interest
                    with connection.cursor() as cursor_1:
                        interests = []
                        if isinstance(r['interest_id'], list):
                            for i_id in r['interest_id']:
                                sql_1 = "SELECT * FROM `interests` WHERE `id`=%s"
                                cursor_1.execute(sql_1, (i_id))
                                r_1 = cursor_1.fetchone()
                                if not r_1:
                                    print 'Interest !!!!', r['name'], i_id
                                else:
                                    interests.append(Interest.objects.get(title=r_1['name']))
                        elif isinstance(r['interest_id'], str):
                            sql_1 = "SELECT * FROM `interests` WHERE `id`=%s"
                            cursor_1.execute(sql_1, (r['interest_id']))
                            r_1 = cursor_1.fetchone()
                            if not r_1:
                                print 'Interest !!!!', r['name'], i_id
                            else:
                                interests.append(Interest.objects.get(title=r_1['name']))

                    # get author
                    with connection.cursor() as cursor_1:
                        user = None
                        sql_1 = "SELECT * FROM `accounts` WHERE `id`=%s"
                        cursor_1.execute(sql_1, (r['creator_id']))
                        r_1 = cursor_1.fetchone()
                        if not r_1:
                            print 'User !!!!', r['name'], r['creator_id']
                        else:
                            user = User.objects.get(username=r_1['email'])

                    # get ages
                    regex = r'(\d+)'
                    min_age = 0
                    max_age = None
                    if '+' in r['age']:
                        min_age = int(re.findall(regex, r['age'])[0])
                    elif ' - ' in r['age']:
                        min_age = int(re.findall(regex, r['age'].split(' - ')[0])[0])
                        max_age = int(re.findall(regex, r['age'].split(' - ')[1])[0])
                    elif '-' in r['age']:
                        min_age = int(re.findall(regex, r['age'].split('-')[0])[0])
                        max_age = int(re.findall(regex, r['age'].split('-')[1])[0])
                    else:
                        _ = re.findall(regex, r['age'])
                        if len(_) > 0:
                            min_age = _[0]

                    # email
                    email = None
                    if EmailField.EMAIL_REGEX.match(r['email']):
                        email = r['email']

                    # web_site
                    web_site = None
                    scheme = r['url'].split('://')[0].lower()
                    if scheme not in URLField._URL_SCHEMES:
                        pass
                    elif URLField._URL_REGEX.match(r['url']):
                        web_site = r['url']

                    i = Event(
                        title=r['name'],
                        city=city,
                        start_date=r['date'],
                        end_date=r['end_date'],
                        interests=interests,
                        author=user,
                        status=statuses[r['status']],
                        address=r['address'],
                        geopoint=(float(r['long']), float(r['latt']), ) if r['long'] and r['latt'] else None,
                        description=r['description'],
                        min_age=min_age,
                        max_age=max_age,
                        phones=[r['phone'], ],
                        email=email,
                        web_site=web_site,
                        type=Event.NORMAL,
                    )
                    i.save()

                    # get picture
                    with connection.cursor() as cursor_1:
                        sql_1 = "SELECT * FROM `pictures` WHERE `event_id`=%s"
                        cursor_1.execute(sql_1, (r['id']))
                        r_1 = cursor_1.fetchone()
                        if not r_1:
                            if r['pic']:
                                FileObject.objects.create(path=r['pic'], entity=i)
                        else:
                            FileObject.objects.create(path=r_1['url'], entity=i)
                    pbar.update(idx + 1)
                pbar.finish()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully imported {} events'.format(len(results))
                    )
                )

            # favorites
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `favorites`"
                cursor.execute(sql)
                results = cursor.fetchall()
                self.stdout.write(
                    self.style.WARNING(
                        'Started importing favorites'
                    )
                )
                pbar = ProgressBar(widgets=[SimpleProgress()], maxval=len(results)).start()
                for idx, r in enumerate(results):
                    user, events = None, None
                    # get event
                    with connection.cursor() as cursor_1:
                        event = None
                        sql_1 = "SELECT * FROM `events` WHERE `id`=%s"
                        cursor_1.execute(sql_1, (r['event_id']))
                        r_1 = cursor_1.fetchone()
                        if not r_1:
                            print 'Event !!!!', r['event_id'], r['account_id']
                        else:
                            events = Event.objects.filter(title=r_1['name'],)

                    # get user
                    with connection.cursor() as cursor_1:
                        user = None
                        sql_1 = "SELECT * FROM `accounts` WHERE `id`=%s"
                        cursor_1.execute(sql_1, (r['account_id']))
                        r_1 = cursor_1.fetchone()
                        if not r_1:
                            print 'User !!!!', r['event_id'], r['account_id']
                        else:
                            user = User.objects.get(username=r_1['email'])

                    if events and user:
                        for event in events:
                            event.add_to_favourites(user)

                    pbar.update(idx + 1)
                pbar.finish()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully imported {} favorites'.format(len(results))
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
