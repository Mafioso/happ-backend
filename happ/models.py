from mongoengine import *

from django.conf import settings

connect(settings.MONGODB_NAME, host=settings.MONGODB_HOST)


class Country(Document):
    date_creatd = DateTimeField()
    name = StringField(required=True)


class City(Document):
    name = StringField(required=True)
    country = ReferenceField(Country, reverse_delete_rule=CASCADE)


class Currency(Document):
    name = StringField(required=True)


class UserSettings(EmbeddedDocument):
    city = ReferenceField(City)
    currency = ReferenceField(Currency)
    notifications = DictField()


class User(Document):
    GENDERS = (MALE, FEMALE) = range(2)

    username = StringField(required=True)
    email = EmailField()
    password = StringField()
    phone = StringField()
    date_of_birth = DateTimeField()
    gender = IntField(choices=GENDERS, default=MALE)
    organization = BooleanField(default=False)
    interests = ListField(ReferenceField('Interest'))
    favorites = ListField(ReferenceField('Event'))
    settings = EmbeddedDocumentField(UserSettings)


class Interest(Document):
    title = StringField()
    is_global = BooleanField(default=True)
    local_cities = ListField(ReferenceField(City))
    parent = ReferenceField('self')


class Event(Document):
    TYPES = (NORMAL, FEATURED, ADS) = range(3)
    STATUSES = (MODERATION, APPROVED, REJECTED) = range(3)

    title = StringField()
    description = StringField()
    type = IntField(choices=TYPES, default=NORMAL)
    status = IntField(choices=STATUSES, default=MODERATION)
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    city = ReferenceField(City, reverse_delete_rule=CASCADE)
    currency = ReferenceField(Currency)
    price = IntField() # we need handle (from .. to ..) scenario
    interests = ListField(ReferenceField(Interest))
    address = StringField()
    geopoint = GeoPointField()
    phones = ListField(StringField())
    email = EmailField()
    web_site = URLField()
    votes = IntField(default=0)

