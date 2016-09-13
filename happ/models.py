# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime

from django.conf import settings
import pymongo
from mongoengine import *
from mongoengine.connection import _get_db
from mongoextensions.fields import DateStringField, TimeStringField
from happ.auth.models import AbstractUser, UserQuerySet


conn = connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)

def get_db():
    return _get_db('default', reconnect=True)

class HappBaseDocument(Document):
    meta = {
        'abstract': True
    }

    date_created = DateTimeField()
    date_edited = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = datetime.now()
        self.date_edited = datetime.now()
        return super(HappBaseDocument, self).save(*args, **kwargs)


class Country(HappBaseDocument):
    name = StringField(required=True)


class City(HappBaseDocument):
    is_active = BooleanField(default=True)
    name = StringField(required=True)
    country = ReferenceField(Country, reverse_delete_rule=CASCADE)

    @property
    def country_name(self):
        if self.country:
            return self.country.name
        return ''


class Currency(HappBaseDocument):
    name = StringField(required=True)


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


class Interest(HappBaseDocument):
    title = StringField()
    is_global = BooleanField(default=True)
    local_cities = ListField(ReferenceField(City))
    parent = ReferenceField('self')
    color = StringField()

    @property
    def children(self):
        return Interest.objects.filter(parent=self)


class Upvote(EmbeddedDocument):
    user = ReferenceField('User')
    ts = DateTimeField(default=datetime.now)


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
    geopoint = GeoPointField()
    phones = ListField(StringField())
    email = EmailField()
    web_site = URLField()
    votes = EmbeddedDocumentListField('Upvote')  # 3200  => {user: date} % 1000
    votes_num = IntField(default=0)
    images = ListField(StringField())
    start_date = DateStringField()
    start_time = TimeStringField()
    end_date = DateStringField()
    end_time = TimeStringField()

    # ATTENTION: add `organizator` field soon

    @property
    def start_datetime(self):
        return datetime.combine(self.start_date, self.start_time).isoformat()

    @property
    def end_datetime(self):
        return datetime.combine(self.end_date, self.end_time).isoformat()

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
