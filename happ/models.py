# -*- coding: utf-8 -*-
import os
import random
import datetime
from copy import deepcopy

from django.conf import settings as django_settings
from mongoengine import *
from mongoengine.connection import _get_db

from mongoextensions.fields import DateStringField, TimeStringField
from happ.auth.models import AbstractUser, UserQuerySet
from .utils import store_file, average_color


conn = connect(django_settings.MONGODB_NAME, host=django_settings.MONGODB_HOST)

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
    geopoint = PointField()

    log_attrs = ('name', )

    @property
    def country_name(self):
        if self.country:
            return self.country.name
        return ''

    @property
    def events_count(self):
        return Event.objects.filter(city=self).count()

    @classmethod
    def get_nearest(cls, geopoint):
        result = City.objects.filter(
            is_active=True,
            geopoint__near=geopoint,
        )
        if result.count() == 0:
            return None
        return result[0]

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
    language = StringField(default=django_settings.HAPP_LANGUAGES[0])


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
    facebook_id = StringField()
    assigned_city = ReferenceField(City, reverse_delete_rule=CASCADE, required=False, null=True)

    quickblox_id = IntField()
    quickblox_password = StringField()
    quickblox_login = StringField()

    log_attrs = ('username', )

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

    @classmethod
    def get_roles_dict(cls):
        return {
            'regular': User.REGULAR,
            'organizer': User.ORGANIZER,
            'moderator': User.MODERATOR,
            'administrator': User.ADMINISTRATOR,
            'root': User.ROOT,
        }

    def get_favourites(self):
        return Event.objects(in_favourites=self, datetimes__0__date__gte=datetime.datetime.now().date())

    def get_feed(self, request):
        #import pdb;pdb.set_trace()
        max_price = 0
        if request.query_params.get('max_price') and int(request.query_params.get('max_price')) == 0:
            max_price = None
        events = Event.objects(
            city=self.settings.city,
            interests__in=self.current_interests,
            type__in=[Event.NORMAL, Event.ADS],
            status=Event.APPROVED,
            datetimes__date__gte=datetime.datetime.now().date(),
            is_active=True,
            max_price__gte=max_price
        )
        feed = Feed.objects(
            event__in=list(events),
            datetimes__date__gte=datetime.datetime.now().date(),
            # datetimes__0__start_time__lte=datetime.datetime.now().strftime('%H%M%S')
            )
        #events = events.aggregate({ '$unwind' : "$datetimes" }, {'$sort': {'datetimes.date':1, 'datetimes.start_time':1}})
        #print(list(events))
        # import pdb;pdb.set_trace()

        return feed

    def get_featured(self):
        return Event.objects(
            city=self.settings.city,
            interests__in=self.current_interests,
            type__in=[Event.FEATURED],
            status=Event.APPROVED,
            datetimes__0__date__gte=datetime.datetime.now().date(),
            is_active=True
        )

    def get_organizer_feed(self):
        return Event.objects(author=self)

    def get_explore(self):
        """
            gets HAPP_EXPLORE_PAGE_SIZE from parent and sibling interests of current interests
        """
        family_interests = [x.family for x in self.current_interests]
        # make it flatten
        interests = [item for sublist in family_interests for item in sublist]

        all_events = Event.objects(city=self.settings.city,
                                   interests__in=interests,
                                   type__in=[Event.NORMAL, Event.ADS],
                                   status=Event.APPROVED,
                                   datetimes__0__date__gte=datetime.datetime.now().date(),
                                   is_active=True)
        if all_events.count() < django_settings.HAPP_EXPLORE_PAGE_SIZE:
            return all_events
        i = random.randint(0, all_events.count() - django_settings.HAPP_EXPLORE_PAGE_SIZE)
        return all_events[i:i + django_settings.HAPP_EXPLORE_PAGE_SIZE]

    def get_map_feed(self, center=None, radius=django_settings.MAP_VIEW_DEFAULT_DISTANCE):
        if center is None:
            return Event.objects.none()
        return Event.objects(
            city=self.settings.city,
            interests__in=self.current_interests,
            type__in=[Event.NORMAL, Event.ADS],
            status=Event.APPROVED,
            is_active=True,
            datetimes__0__date__gte=datetime.datetime.now().date(),
            geopoint__geo_within_sphere=[center, radius / django_settings.EARTH_RADIUS],
        )

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

    def assign_city(self, city):
        self.assigned_city = city
        self.save()


class Interest(HappBaseDocument):
    title = StringField()
    is_global = BooleanField(default=True)
    local_cities = ListField(ReferenceField(City))
    parent = ReferenceField('self')
    is_active = BooleanField(default=True)

    log_attrs = ('title', )

    @property
    def children(self):
        return Interest.objects.filter(parent=self)

    @property
    def siblings(self):
        if self.parent:
            return self.parent.children
        return []

    @property
    def family(self):
        if self.parent:
            return [self.parent] + list(self.siblings)
        else:
            return [self] + list(self.children)

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


class RejectionReason(HappBaseDocument):
    event = ReferenceField('Event')
    author = ReferenceField('User')
    text = StringField()


class Event(HappBaseDocument):
    TYPES = (NORMAL, FEATURED, ADS) = range(3)
    STATUSES = (MODERATION, APPROVED, REJECTED) = range(3)

    localized_fields = ('title', )

    title = StringField()
    description = StringField()
    language = StringField(default=django_settings.HAPP_LANGUAGES[0]) # en ru fr it es de
    type = IntField(choices=TYPES, default=NORMAL)
    status = IntField(choices=STATUSES, default=MODERATION)
    is_active = BooleanField(default=True)
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    city = ReferenceField(City, reverse_delete_rule=CASCADE, required=False)
    currency = ReferenceField(Currency, required=False)
    min_price = IntField()
    max_price = IntField()
    interests = ListField(ReferenceField('Interest'))
    in_favourites = ListField(ReferenceField('User'))
    address = StringField()
    place_name = StringField()
    geopoint = PointField()
    phones = ListField(StringField())
    email = EmailField()
    web_site = URLField()
    datetimes = EmbeddedDocumentListField('EventTime')
    votes = EmbeddedDocumentListField('Upvote')  # 3200  => {user: date} % 1000
    votes_num = IntField(default=0)
    close_on_start = BooleanField(default=False)
    registration_link = StringField()
    tickets_link = StringField()
    min_age = IntField(default=0)
    max_age = IntField(default=200)

    log_attrs = ('title', )

    ## TEMP
    _random = IntField()

    # ATTENTION: add `organizator` field soon

    # meta = {
    #     'indexes': [("geopoint", "2dsphere")]
    # }

    @property
    def start_datetime(self):
        return datetime.datetime.combine(self.start_date, self.start_time or datetime.time()).isoformat()

    @property
    def end_datetime(self):
        return datetime.datetime.combine(self.end_date, self.end_time or datetime.time()).isoformat()

    @property
    def images(self):
        return FileObject.objects.filter(entity=self)

    @property
    def complaints(self):
        return Complaint.objects.filter(event=self)

    @property
    def rejection_reasons(self):
        return RejectionReason.objects.filter(event=self).order_by('-date_created')

    def localized(self, language=django_settings.HAPP_LANGUAGES[0]):
        try:
            return Localized.objects.get(entity=self, language=language)
        except:
            return None

    def copy(self):
        new_instance = deepcopy(self)
        new_instance.id = None
        new_instance.status = Event.MODERATION
        new_instance.in_favourites = []
        new_instance.votes = []
        new_instance.votes_num = 0
        new_instance.save()
        return new_instance

    def translate(self, language=None):
        from .tasks import translate_entity
        if language:
            translate_entity.delay(cls=self.__class__, id=self.id, target=language)
        else:
            for language in django_settings.HAPP_LANGUAGES:
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

    def reject(self, text, author):
        self.status = Event.REJECTED
        self.save()
        rr = RejectionReason(text=text, author=author, event=self)
        rr.save()

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

class Feed(HappBaseDocument):
    event = ReferenceField(Event, reverse_delete_rule=CASCADE)
    datetimes = EmbeddedDocumentListField('EventTime')

class EventTime(EmbeddedDocument):
    date = DateStringField()
    start_time = TimeStringField()
    end_time = TimeStringField()


class FileObject(HappBaseDocument):
    path = StringField()
    entity = GenericReferenceField()
    color = StringField()

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        os.remove(document.path)

    def move_to_media(self, entity):
        self.entity = entity
        self.path = store_file(self.path, django_settings.NGINX_UPLOAD_ROOT, str(self.entity.id))
        self.recalculate_color()
        self.save()

    def move_to_avatar(self, entity):
        self.entity = entity
        self.path = store_file(self.path, django_settings.NGINX_AVATAR_ROOT, str(self.entity.id))
        self.recalculate_color()
        self.save()

    def move_to_misc(self, entity):
        self.entity = entity
        self.path = store_file(self.path, django_settings.NGINX_MISC_ROOT, str(self.entity.id))
        self.recalculate_color()
        self.save()

    def recalculate_color(self):
        self.color = average_color(self.path)
        self.save()


class Localized(Document):
    language = StringField(default=django_settings.HAPP_LANGUAGES[0])
    data = DictField()
    entity = GenericReferenceField()


class Complaint(HappBaseDocument):
    STATUSES = OPEN, CLOSED = range(2)

    text = StringField()
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    status = IntField(choices=STATUSES, default=OPEN)
    answer = StringField()
    date_answered = DateTimeField()
    executor = ReferenceField(User, reverse_delete_rule=CASCADE)
    event = ReferenceField(Event, reverse_delete_rule=CASCADE)

    log_attrs = ('text', )

    def reply(self, answer, executor):
        self.answer = answer
        self.executor = executor
        self.date_answered = datetime.datetime.now()
        self.status = Complaint.CLOSED
        self.save()


class FeedbackMessage(HappBaseDocument):

    text = StringField()
    author = ReferenceField(User, reverse_delete_rule=CASCADE)


class StaticText(HappBaseDocument):
    TYPES = TERMS_OF_SERVICE, PRIVACY_POLICY, ORGANIZER_RULES, FAQ = range(4)

    text = StringField()
    type = IntField(choices=TYPES, default=TERMS_OF_SERVICE)

    log_attrs = ('type', )

    @classmethod
    def title(cls, type):
        titles = {
            StaticText.TERMS_OF_SERVICE: u'Правила пользования',
            StaticText.PRIVACY_POLICY: u'Политика конфиденциальности',
            StaticText.ORGANIZER_RULES: u'Правила организатора события',
            StaticText.FAQ: u'Вопросы-ответы',
        }
        return titles[type]



class LogEntry(HappBaseDocument):
    """
        city:
            - name
        interest
            - title
        user
            - username
        event
            - title
        complaint
            - text
        static_text
            - type
    """
    FLAGS = ADDITION, CHANGE, DELETION, APPROVAL, REJECTION, ACTIVATION, DEACTIVATION, REPLY = range(8)

    entity = GenericReferenceField()
    data = DictField()
    flag = IntField(choices=FLAGS, default=ADDITION)
    author = ReferenceField(User, reverse_delete_rule=CASCADE)

    @property
    def text(self):
        flag_texts = {
            LogEntry.ADDITION: u'Создание',
            LogEntry.CHANGE: u'Изменение',
            LogEntry.DELETION: u'Удаление',
            LogEntry.APPROVAL: u'Утверждение',
            LogEntry.REJECTION: u'Отклонение',
            LogEntry.ACTIVATION: u'Активация',
            LogEntry.DEACTIVATION: u'Деактивация',
            LogEntry.REPLY: u'Ответ',
        }
        if self.entity.__class__ == City:
            return u'{flag} города {name}'.format(flag=flag_texts[self.flag], name=self.data['name'])
        if self.entity.__class__ == User:
            return u'{flag} пользователя {username}'.format(flag=flag_texts[self.flag], username=self.data['username'])
        if self.entity.__class__ == Interest:
            return u'{flag} интереса {title}'.format(flag=flag_texts[self.flag], title=self.data['title'])
        if self.entity.__class__ == Event:
            return u'{flag} события {title}'.format(flag=flag_texts[self.flag], title=self.data['title'])
        if self.entity.__class__ == Complaint:
            return u'{flag} на жалобу {text}'.format(flag=flag_texts[self.flag], text=self.data['text'])
        if self.entity.__class__ == StaticText:
            return u'{flag} статичной страницы {type}'.format(flag=flag_texts[self.flag], type=StaticText.titles(self.data['type']))
        return ''


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
