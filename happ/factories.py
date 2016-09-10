import random
import factory
from faker import Factory as FakerFactory

from models import (
    User,
    UserSettings,
    City,
    Currency,
    Upvote,
    Interest,
    Event,
    Localized,
    CityInterests
)

ALL_CITIES = City.objects
ALL_CURRENCIES = Currency.objects

faker = FakerFactory.create()


class CityFactory(factory.mongoengine.MongoEngineFactory):
    name = factory.Faker('word')

    class Meta:
        model = City


class CurrencyFactory(factory.mongoengine.MongoEngineFactory):
    name = factory.Faker('word')

    class Meta:
        model = Currency


class UserSettingsFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = UserSettings

    # city = factory.LazyAttribute(lambda x: random.choice(ALL_CITIES) if ALL_CITIES.count() > 5 else None)
    # currency = factory.LazyAttribute(lambda x: random.choice(ALL_CURRENCIES) if ALL_CURRENCIES.count() > 5 else None)


class CityInterestsFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = CityInterests


class UserFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda x: faker.user_name() + u" ".join(faker.words()))
    email = factory.LazyAttribute(lambda x: u"".join(faker.words()) + u"_" +  faker.email())
    settings = factory.SubFactory(UserSettingsFactory)

    @factory.lazy_attribute
    def interests(self):
        cities = [City.objects.first() for _ in xrange(random.randint(2, 4))]
        return [CityInterests(c=city, ins=[Interest.objects.first() for _ in xrange(random.randint(0, 3))]) for city in cities]


class InterestFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Interest

    title = factory.Faker('word')
    is_global = factory.LazyAttribute(lambda x: random.choice((True, False,)))
    local_cities = factory.LazyAttribute(lambda x: random.sample(ALL_CITIES, random.randint(0, 5)) if not x.is_global and ALL_CITIES.count() > 5 else [])

    @factory.lazy_attribute
    def parent(self):
        if not self.is_global:
            global_interests = Interest.objects(is_global=True)
            return random.choice(global_interests) if len(global_interests) > 0 else None
        return None


class UpvoteFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Upvote


class EventFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Event

    title = factory.Faker('word')
    description = factory.Faker('sentence')
    author = factory.LazyAttribute(lambda x: User.objects.first())
    city = factory.LazyAttribute(lambda x: random.choice(ALL_CITIES) if ALL_CITIES.count() > 0 else None)
    currency = factory.LazyAttribute(lambda x: random.choice(ALL_CURRENCIES) if ALL_CURRENCIES.count() > 0 else None)
    min_price = factory.Faker('pyint')
    max_price = factory.Faker('pyint')
    address = factory.Faker('street_address')
    # phones =
    email = factory.Faker('email')
    web_site = factory.Faker('url')
    # votes = factory.Faker('pyint')
    start_date = factory.Faker('date_time')
    start_time = factory.Faker('date_time')
    end_date = factory.Faker('date_time')
    end_time = factory.Faker('date_time')

    # def geopoint(self):
    #     print factory.Faker('longitude'), factory.Faker('latitude'),
    #     return (factory.Faker('longitude'), factory.Faker('latitude'),)

    @factory.lazy_attribute
    def interests(self):
        interests = Interest.objects()
        if interests.count() < 3:
            return []
        return random.sample(interests, random.randint(1,3))

    @factory.lazy_attribute
    def votes(self):
        num_users = User.objects.count() % 100
        if num_users == 0:
            return []
        users = random.sample(User.objects(), random.randint(1, num_users) - 1)
        return [Upvote(user=u, ts=faker.date_time()) for u in users]

    @factory.lazy_attribute
    def votes_num(self):
        return len(self.votes)


class LocalizedFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Localized
