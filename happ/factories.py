import random
import factory

from models import (
    User,
    UserSettings,
    City,
    Currency,
    Interest,
    Event,
)

ALL_CITIES = City.objects
ALL_CURRENCIES = Currency.objects


class EventFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Event

    title = factory.Faker('word')
    description = factory.Faker('sentence')
    author = factory.LazyAttribute(lambda x: User.objects.first())
    city = factory.LazyAttribute(lambda x: random.choice(ALL_CITIES) if ALL_CITIES.count() > 0 else None)
    currency = factory.LazyAttribute(lambda x: random.choice(ALL_CURRENCIES) if ALL_CURRENCIES.count() > 0 else None)
    price = factory.Faker('pyint')
    address = factory.Faker('street_address')
    # phones = 
    email = factory.Faker('email')
    web_site = factory.Faker('url')
    votes = factory.Faker('pyint')

    # def geopoint(self):
    #     print factory.Faker('longitude'), factory.Faker('latitude'),
    #     return (factory.Faker('longitude'), factory.Faker('latitude'),)

    @factory.lazy_attribute
    def interests(self):
        interests = Interest.objects()
        if interests.count() < 3:
            return []
        return random.sample(interests, random.randint(1,3))
