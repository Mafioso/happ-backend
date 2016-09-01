from datetime import datetime
from mongoengine import *

from django.conf import settings

from mongoextensions.fields import DateStringField, TimeStringField
from happ.auth.models import AbstractUser, UserQuerySet


connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)


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
    name = StringField(required=True)
    country = ReferenceField(Country, reverse_delete_rule=CASCADE)


class Currency(HappBaseDocument):
    name = StringField(required=True)


class UserSettings(EmbeddedDocument):
    city = ReferenceField(City)
    currency = ReferenceField(Currency)
    notifications = DictField()
    language = StringField(default=settings.HAPP_LANGUAGES[0])


class User(AbstractUser, HappBaseDocument):
    meta = {
        'queryset_class': UserQuerySet
    }
    GENDERS = (MALE, FEMALE) = range(2)

    username = StringField(required=True)
    fullname = StringField()
    email = EmailField()
    password = StringField()
    phone = StringField()
    date_of_birth = DateTimeField()
    gender = IntField(choices=GENDERS, default=MALE)
    organization = BooleanField(default=False)
    interests = ListField(ReferenceField('Interest'))
    favorites = ListField(ReferenceField('Event'))
    settings = EmbeddedDocumentField(UserSettings)
    is_active = BooleanField(default=True)
    last_login = DateTimeField(blank=True, null=True)

    @property
    def fn(self):
        return self.fullname if self.fullname else self.username


class Interest(HappBaseDocument):
    title = StringField()
    is_global = BooleanField(default=True)
    local_cities = ListField(ReferenceField(City))
    parent = ReferenceField('self')
    color = StringField()

    @property
    def children(self):
        return Interest.objects.filter(parent=self)


class Event(HappBaseDocument):
    TYPES = (NORMAL, FEATURED, ADS) = range(3)
    STATUSES = (MODERATION, APPROVED, REJECTED) = range(3)

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
    interests = ListField(ReferenceField(Interest))
    address = StringField()
    geopoint = GeoPointField()
    phones = ListField(StringField())
    email = EmailField()
    web_site = URLField()
    votes = IntField(default=0)
    start_date = DateStringField()
    start_time = TimeStringField()
    end_date = DateStringField()
    end_time = TimeStringField()

    def localized(self, language=settings.HAPP_LANGUAGES[0]):
        try:
            return Localized.objects.get(language=language)
        except:
            return None


class Localized(Document):
    language = StringField(default=settings.HAPP_LANGUAGES[0])
    data = DictField()
    entity = GenericReferenceField()
