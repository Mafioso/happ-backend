# -*- coding: utf-8 -*-
import os
import datetime
from copy import deepcopy

from django.conf import settings
from mongoengine import *
from mongoengine.connection import _get_db

from mongoextensions.fields import DateStringField, TimeStringField
from happ.auth.models import AbstractUser, UserQuerySet
from .utils import store_file, average_color


conn = connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)

def get_db():
    return _get_db('default', reconnect=True)

class HappBaseDocument(Document):
    meta = {
        'abstract': True
    }

    date_created = DateTimeField()
    date_edited = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = datetime.datetime.now()
        self.date_edited = datetime.datetime.now()
        return super(HappBaseDocument, self).save(*args, **kwargs)


class Currency(HappBaseDocument):
    name = StringField(required=True)
    code = StringField(required=True)


class Country(HappBaseDocument):
    name = StringField(required=True)
    currency = ReferenceField(Currency, reverse_delete_rule=CASCADE)


class City(HappBaseDocument):
    is_active = BooleanField(default=True)
    name = StringField(required=True)
    country = ReferenceField(Country, reverse_delete_rule=CASCADE)
    geopoint = GeoPointField()

    @property
    def country_name(self):
        if self.country:
            return self.country.name
        return ''

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()


class UserSettings(EmbeddedDocument):
    city = ReferenceField('City')
    currency = ReferenceField('Currency')
    notifications = DictField()
    language = StringField(default=settings.HAPP_LANGUAGES[0])


class CityInterests(EmbeddedDocument):
    c = ReferenceField('City')
    ins = ListField(ReferenceField('Interest'))


class User(AbstractUser, HappBaseDocument):
    meta = {
        'queryset_class': UserQuerySet
    }
    GENDERS = (MALE, FEMALE) = range(2)
    ROLES = (REGULAR, ORGANIZER, MODERATOR, ADMINISTRATOR, ROOT) = range(5)

    username = StringField(required=True, unique=True)
    fullname = StringField()
    email = EmailField()
    password = StringField()
    phone = StringField()
    date_of_birth = DateTimeField()
    gender = IntField(choices=GENDERS, default=MALE)
    organization = BooleanField(default=False)
    interests = EmbeddedDocumentListField('CityInterests')
    settings = EmbeddedDocumentField(UserSettings)
    is_active = BooleanField(default=True)
    last_login = DateTimeField(blank=True, null=True)
    role = IntField(choices=ROLES, default=REGULAR)
    confirmation_key = StringField()
    confirmation_key_expires = DateTimeField(blank=True, null=True)

    @property
    def fn(self):
        return self.fullname if self.fullname else self.username

    @property
    def current_interests(self):
        if not self.settings.city:
            return []
        try:
            ci = self.interests.get(c=self.settings.city)
            return ci.ins
        except:
            return []

    @property
    def avatar(self):
        try:
            return FileObject.objects.get(entity=self)
        except FileObject.DoesNotExist:
            return None

    def get_favourites(self):
        return Event.objects(in_favourites=self)

    def get_feed(self):
        return Event.objects(city=self.settings.city, interests__in=self.current_interests, type__in=[Event.NORMAL, Event.ADS], status=Event.APPROVED)

    def get_featured(self):
        return Event.objects(city=self.settings.city, interests__in=self.current_interests, type__in=[Event.FEATURED], status=Event.APPROVED)

    def get_organizer_feed(self):
        return Event.objects(author=self)

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()


class Interest(HappBaseDocument):
    title = StringField()
    is_global = BooleanField(default=True)
    local_cities = ListField(ReferenceField(City))
    parent = ReferenceField('self')
    is_active = BooleanField(default=True)

    @property
    def children(self):
        return Interest.objects.filter(parent=self)

    @property
    def image(self):
        try:
            return FileObject.objects.get(entity=self)
        except FileObject.DoesNotExist:
            return None

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()


class Upvote(EmbeddedDocument):
    user = ReferenceField('User')
    ts = DateTimeField(default=datetime.datetime.now)


class Event(HappBaseDocument):
    TYPES = (NORMAL, FEATURED, ADS) = range(3)
    STATUSES = (MODERATION, APPROVED, REJECTED) = range(3)

    localized_fields = ('title', )

    title = StringField()
    description = StringField()
    language = StringField(default=settings.HAPP_LANGUAGES[0]) # en ru fr it es de
    type = IntField(choices=TYPES, default=NORMAL)
    status = IntField(choices=STATUSES, default=MODERATION)
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    city = ReferenceField(City, reverse_delete_rule=CASCADE, required=False)
    currency = ReferenceField(Currency, required=False)
    min_price = IntField()
    max_price = IntField()
    interests = ListField(ReferenceField('Interest'))
    in_favourites = ListField(ReferenceField('User'))
    address = StringField()
    place_name = StringField()
    geopoint = GeoPointField()
    phones = ListField(StringField())
    email = EmailField()
    web_site = URLField()
    votes = EmbeddedDocumentListField('Upvote')  # 3200  => {user: date} % 1000
    votes_num = IntField(default=0)
    start_date = DateStringField()
    start_time = TimeStringField()
    end_date = DateStringField()
    end_time = TimeStringField()
    close_on_start = BooleanField(default=False)
    registration_link = StringField()
    min_age = IntField(default=0)
    max_age = IntField(default=200)

    ## TEMP
    _random = IntField()

    # ATTENTION: add `organizator` field soon

    @property
    def start_datetime(self):
        return datetime.datetime.combine(self.start_date, self.start_time or datetime.time()).isoformat()

    @property
    def end_datetime(self):
        return datetime.datetime.combine(self.end_date, self.end_time or datetime.time()).isoformat()

    @property
    def images(self):
        return FileObject.objects.filter(entity=self)

    def localized(self, language=settings.HAPP_LANGUAGES[0]):
        try:
            return Localized.objects.get(entity=self, language=language)
        except:
            return None

    def copy(self):
        new_instance = deepcopy(self)
        new_instance.id = None
        new_instance.save()
        return new_instance

    def translate(self, language=None):
        from .tasks import translate_entity
        if language:
            translate_entity.delay(cls=self.__class__, id=self.id, target=language)
        else:
            for language in settings.HAPP_LANGUAGES:
                translate_entity.delay(cls=self.__class__, id=self.id, target=language)

    def is_upvoted(self, user):
        try:
            vote = self.votes.get(user=user)
            return vote
        except:
            return False

    def upvote(self, user):
        if self.is_upvoted(user):
            return False
        upvote = Upvote(user=user)
        self.update(push__votes=upvote, inc__votes_num=1)
        return True

    def downvote(self, user):
        vote = self.is_upvoted(user)
        if not vote:
            return False
        self.update(pull__votes=vote, dec__votes_num=1)
        return True

    def add_to_favourites(self, user):
        if self.is_in_favourites(user):
            return False
        self.update(add_to_set__in_favourites=user)
        return True

    def is_in_favourites(self, user):
        return user in self.in_favourites

    def remove_from_favourites(self, user):
        if not self.is_in_favourites(user):
            return False
        self.update(pull__in_favourites=user)
        return True

    def approve(self):
        self.status = Event.APPROVED
        self.save()

    def reject(self):
        self.status = Event.REJECTED
        self.save()


class FileObject(HappBaseDocument):
    path = StringField()
    entity = GenericReferenceField()
    color = StringField()

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        os.remove(document.path)

    def move_to_media(self, entity):
        self.entity = entity
        self.path = store_file(self.path, settings.NGINX_UPLOAD_ROOT, str(self.entity.id))
        self.recalculate_color()
        self.save()

    def move_to_avatar(self, entity):
        self.entity = entity
        self.path = store_file(self.path, settings.NGINX_AVATAR_ROOT, str(self.entity.id))
        self.recalculate_color()
        self.save()

    def move_to_misc(self, entity):
        self.entity = entity
        self.path = store_file(self.path, settings.NGINX_MISC_ROOT, str(self.entity.id))
        self.recalculate_color()
        self.save()

    def recalculate_color(self):
        self.color = average_color(self.path)
        self.save()


class Localized(Document):
    language = StringField(default=settings.HAPP_LANGUAGES[0])
    data = DictField()
    entity = GenericReferenceField()


# Notification
#  - text
#  - receivers
#  - ts

# Доставка уведомлений в ленту

# 1. Добавление нового события
#     - по событию id вытаскиваем всех пользователей id у которых данное событие в избранном
#     - делаем рассылку push в специальную "раковину"

# 2. Upvote события
#     - по событию id вытаскиваем всех пользователей id у которых данное событие в избранном
#     - рассылаем информацию о том что пользователь такой-то сделал upvote события такого-то

# 4. Изменение даты окончания события
#     - по событию id вытаскиваем всех пользователей id у которых данное событие в избранном
#     - рассылаем информацию о том что дата окончания такого-то события изменилась

# Внимание: добавить организатора ко всем


# Notification
#  - text
#  - receivers
#  - ts
