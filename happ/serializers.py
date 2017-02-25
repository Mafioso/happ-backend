import json
from datetime import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers as drf_serializers
from rest_framework.exceptions import ValidationError
from rest_framework_mongoengine import serializers

from mongoextensions.filters.fields import GeoPointField

from happ.utils import string_to_date, make_random_password
from happ.integrations.quickblox import signup as quickblox_signup
from happ.integrations import yahoo

from .models import (
    Country,
    City,
    Currency,
    User,
    UserSettings,
    Interest,
    Event,
    FileObject,
    Complaint,
    RejectionReason,
    FeedbackMessage,
    EventTime,
    LogEntry,
    Feed,
)


class LocalizedSerializer(serializers.DocumentSerializer):

    def to_representation(self, instance):
        data = super(LocalizedSerializer, self).to_representation(instance)
        if 'request' not in self.context:
            return data
        language = self.context['request'].user.settings.language
        localized_instance = instance.localized(language=language)
        if not localized_instance:
            return data
        if hasattr(self.Meta.model, 'localized_fields') and self.Meta.model.localized_fields:
            for field in self.Meta.model.localized_fields:
                if field in localized_instance.data:
                    data[field] = localized_instance.data[field]
        return data


class FileObjectSerializer(serializers.DocumentSerializer):

    class Meta:
        model = FileObject
        fields = (
            'id',
            'path',
            'color',
        )


class CurrencySerializer(serializers.DocumentSerializer):

    class Meta:
        model = Currency
        exclude = (
            'date_created',
            'date_edited',
        )


class CountrySerializer(serializers.DocumentSerializer):
    currency = CurrencySerializer()

    class Meta:
        model = Country
        exclude = (
            'date_created',
            'date_edited',
        )


class CitySerializer(serializers.DocumentSerializer):
    # read only fields
    country_name = drf_serializers.CharField(read_only=True)
    geopoint = GeoPointField(read_only=True)

    # write only fields
    country_id = serializers.ObjectIdField(write_only=True)
    geopoint_lng = drf_serializers.FloatField(write_only=True, required=False)
    geopoint_lat = drf_serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = City
        exclude = (
            'date_created',
            'date_edited',
            'country',
        )

    def create(self, validated_data):
        country_id = validated_data.pop('country_id')
        geopoint_lng = validated_data.pop('geopoint_lng') if 'geopoint_lng' in validated_data else None
        geopoint_lat = validated_data.pop('geopoint_lat') if 'geopoint_lat' in validated_data else None

        city = City.objects.create(**validated_data)
        if geopoint_lng and geopoint_lat:
            city.geopoint = (geopoint_lng, geopoint_lat, )
        country = Country.objects.get(id=country_id)
        city.country = country
        city.save()
        return city

    def update(self, instance, validated_data):
        country_id = validated_data.pop('country_id')
        city = super(CitySerializer, self).update(instance, validated_data)
        if 'geopoint_lng' in validated_data and 'geopoint_lat' in validated_data:
            geopoint_lng = validated_data.pop('geopoint_lng')
            geopoint_lat = validated_data.pop('geopoint_lat')
            city.geopoint = (geopoint_lng, geopoint_lat, )
        country = Country.objects.get(id=country_id)
        city.country = country
        city.save()
        return city


class InterestSerializer(serializers.DocumentSerializer):
    # read only fields
    parent = serializers.ReferenceField(read_only=True)
    image = drf_serializers.SerializerMethodField()

    # write only fields
    is_global = drf_serializers.BooleanField(write_only=True)
    parent_id = serializers.ObjectIdField(write_only=True, allow_null=True)
    local_cities = drf_serializers.ListField(write_only=True)
    image_id = drf_serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Interest
        exclude = (
            'date_created',
            'date_edited',
        )

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id') if 'parent_id' in validated_data else None
        local_cities = validated_data.pop('local_cities') if 'local_cities' in validated_data else []
        image_id = validated_data.pop('image_id') if 'image_id' in validated_data else None
        interest = Interest.objects.create(**validated_data)
        if parent_id:
            parent = Interest.objects.get(id=parent_id)
            interest.parent = parent
        local_cities = City.objects.filter(id__in=local_cities)
        interest.local_cities = local_cities
        interest.save()
        if image_id:
            image = FileObject.objects.get(id=image_id)
            image.move_to_misc(entity=interest)
        return interest

    def update(self, instance, validated_data):
        parent_id = validated_data.pop('parent_id') if 'parent_id' in validated_data else None
        image_id = validated_data.pop('image_id') if 'image_id' in validated_data else None
        local_cities = None
        if validated_data.get('local_cities'):
            local_cities = validated_data.pop('local_cities') if 'local_cities' in validated_data else []
        interest = super(InterestSerializer, self).update(instance, validated_data)
        if parent_id:
            parent = Interest.objects.get(id=parent_id)
            interest.parent = parent
        if local_cities:
            local_cities = City.objects.filter(id__in=local_cities)
            interest.local_cities = local_cities
        interest.save()
        if image_id:
            if interest.image:
                interest.image.delete()
            image = FileObject.objects.get(id=image_id)
            image.move_to_misc(entity=interest)
        return interest

    def get_image(self, obj):
        if not obj.image:
            return None
        return FileObjectSerializer(obj.image).data


class InterestChildSerializer(serializers.DocumentSerializer):
    # regular fields
    parent = InterestSerializer()
    local_cities = CitySerializer(many=True)

    class Meta:
        model = Interest
        exclude = (
            'date_created',
            'date_edited',
        )

class InterestParentSerializer(serializers.DocumentSerializer):
    # regular fields
    children = InterestSerializer(many=True)

    # read only fields
    image = drf_serializers.SerializerMethodField()

    class Meta:
        model = Interest
        exclude = (
            'date_created',
            'date_edited',
            'is_global',
            'local_cities',
        )

    def get_image(self, obj):
        if not obj.image:
            return None
        return FileObjectSerializer(obj.image).data


class UserSettingsSerializer(serializers.EmbeddedDocumentSerializer):

    class Meta:
        model = UserSettings


class UserSerializer(serializers.DocumentSerializer):
    # read only fields
    fn = drf_serializers.CharField(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    avatar = FileObjectSerializer(read_only=True)

    # write only fields
    avatar_id = drf_serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True}
        }
        exclude = (
            'interests',
            'assigned_city',
        )

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        if 'password' in validated_data: # if registered with facebook there is no password
            user.set_password(validated_data['password'])
        user.settings = UserSettings()
        user.save()
        quickblox_password = make_random_password()
        quickblox_user = quickblox_signup(user.username, quickblox_password, facebook_id=user.facebook_id, email=user.email)
        # import pdb;pdb.set_trace()
        if 'errors' not in quickblox_user:
            user.quickblox_id = str(quickblox_user['user']['id'])
            user.quickblox_login = str(quickblox_user['user']['login'])
            user.quickblox_password = quickblox_password
            user.save()
        return user

    def update(self, instance, validated_data):
        user = super(UserSerializer, self).update(instance, validated_data)

        if 'avatar_id' in validated_data:
            avatar_id = validated_data.pop('avatar_id')
            if instance.avatar and instance.avatar.id:
                FileObject.objects.filter(id__in=(instance.avatar.id,)).delete()
            try:
                FileObject.objects.get(id=avatar_id).move_to_avatar(entity=user)
            except Exception as e:
                print e
                pass

        user.save()
        return user


class UserAdminSerializer(serializers.DocumentSerializer):
    # read only fields
    fn = drf_serializers.CharField(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    avatar = FileObjectSerializer(read_only=True)
    assigned_city = CitySerializer(read_only=True)

    # write only fields
    avatar_id = drf_serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True}
        }
        exclude = (
            'interests',
        )

    def create(self, validated_data):
        user = super(UserAdminSerializer, self).create(validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        else:
            user.set_password('123456') # by default for staff users (when created in admin page)
        user.settings = UserSettings()
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super(UserAdminSerializer, self).update(instance, validated_data)

        if 'avatar_id' in validated_data:
            avatar_id = validated_data.pop('avatar_id')
            if instance.avatar and instance.avatar.id:
                FileObject.objects.filter(id__in=(instance.avatar.id,)).delete()
            try:
                FileObject.objects.get(id=avatar_id).move_to_avatar(entity=user)
            except:
                pass

        user.save()
        return user


class UserPayloadSerializer(serializers.DocumentSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
        )


class AuthorSerializer(serializers.DocumentSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'fn',
            'quickblox_id'
        )


class RejectionReasonSerializer(serializers.DocumentSerializer):
    author = AuthorSerializer()

    class Meta:
        model = RejectionReason


class EventTimeSerializer(serializers.EmbeddedDocumentSerializer):

    class Meta:
        model = EventTime


class EventSerializer(LocalizedSerializer):
    geopoint = GeoPointField()
    #datetimes = EventTimeSerializer(many=True, required=False)
    #datetimes = drf_serializers.SerializerMethodField()
    #datetime = drf_serializers.SerializerMethodField()

    # read only fields
    interests = InterestChildSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    rejection_reason = drf_serializers.SerializerMethodField()
    is_upvoted = drf_serializers.SerializerMethodField()
    is_in_favourites = drf_serializers.SerializerMethodField()
    images = drf_serializers.SerializerMethodField()
    is_active = drf_serializers.BooleanField(read_only=True)

    # write only fields
    interest_ids = drf_serializers.ListField(write_only=True, required=False)
    currency_id = serializers.ObjectIdField(write_only=True, required=False)
    city_id = serializers.ObjectIdField(write_only=True, required=False)
    image_ids = drf_serializers.ListField(write_only=True, required=False)
    datetimes = EventTimeSerializer( many=True, required=False)

    class Meta:
        model = Event
        exclude = (
            'votes',
            'in_favourites',
        )

    def validate_city_id(self, value):
        try:
            city = City.objects.get(id=value)
        except City.DoesNotExist:
            raise ValidationError(_('No city with this city_id'))
        except City.MultipleObjectsReturned:
            raise ValidationError(_('Too many cities with this city_id'))
        return city

    def validate_currency_id(self, value):
        try:
            currency = Currency.objects.get(id=value)
        except Currency.DoesNotExist:
            raise ValidationError(_('No currency with this currency_id'))
        except Currency.MultipleObjectsReturned:
            raise ValidationError(_('Too many currencies with this currency_id'))
        return currency


    def validate(self, data):
        """
        Min_price should be less than Max_price.
        """
        if 'min_price' in data and 'max_price' in data and data['min_price'] > data['max_price']:
            raise ValidationError(_("Min_price should be less than Max_price"))
        return data

    def create(self, validated_data):
        city = validated_data.pop('city_id')
        currency = validated_data.pop('currency_id')
        interest_ids = validated_data.pop('interest_ids') if 'interest_ids' in validated_data else []
        image_ids = validated_data.pop('image_ids') if 'image_ids' in validated_data else []
        author = validated_data.pop('author')
        datetimes = validated_data.pop('datetimes')
        event = super(EventSerializer, self).create(validated_data)

        event.city = city
        event.currency = currency
        event.author = author
        event.interests = Interest.objects.filter(id__in=interest_ids)
        [event.datetimes.append(datetime) for datetime in datetimes]
        event.save()

        map(lambda x: x.move_to_media(entity=event), FileObject.objects.filter(id__in=image_ids))
        #event.translate()
        event.create_feed()
        return event

    def update(self, instance, validated_data):
        datetimes = validated_data.pop('datetimes') if 'datetimes' in validated_data else None
        event = super(EventSerializer, self).update(instance, validated_data)

        if datetimes:
            event.datetimes.delete()
            [event.datetimes.append(datetime) for datetime in datetimes]
        if 'city_id' in validated_data:
            city = validated_data.pop('city_id')
            event.city = city
        if 'currency_id' in validated_data:
            currency = validated_data.pop('currency_id')
            event.currency = currency
        if 'interest_ids' in validated_data:
            interest_ids = validated_data.pop('interest_ids')
            event.interests = Interest.objects.filter(id__in=interest_ids)
        if 'image_ids' in validated_data:
            image_ids = set(validated_data.pop('image_ids'))
            old_ids = set(map(lambda x: str(x.id), instance.images))
            FileObject.objects.filter(id__in=(old_ids-image_ids)).delete()
            map(lambda x: x.move_to_media(entity=event), FileObject.objects.filter(id__in=(image_ids-old_ids)))

        event.status = Event.MODERATION
        event.save()
        #event.translate()
        event.create_feed()
        return event

    def get_is_upvoted(self, obj):
        if 'request' not in self.context:
            return False
        return bool(obj.is_upvoted(self.context['request'].user))

    def get_is_in_favourites(self, obj):
        if 'request' not in self.context:
            return False
        return obj.is_in_favourites(self.context['request'].user)

    def get_images(self, obj):
        return FileObjectSerializer(obj.images, many=True).data

    def get_datetimes(self, obj):
        datetimes = []
        for item in obj['datetimes']:
            if string_to_date(str(item['date']), settings.DATE_STRING_FIELD_FORMAT) >= datetime.now().date():
                datetimes.append(item)
        return EventTimeSerializer(datetimes, many=True, required=False).data

    # def get_datetime(self, obj):
    #     datetimes = []
    #     for item in obj['datetimes']:
    #         if string_to_date(str(item['date']), settings.DATE_STRING_FIELD_FORMAT) >= datetime.now().date():
    #             datetimes.append(item)
    #             break
    #     return EventTimeSerializer(datetimes, many=True, required=False).data

    def get_rejection_reason(self, obj):
        if obj.rejection_reasons.count() == 0:
            return None
        return RejectionReasonSerializer(obj.rejection_reasons[0]).data

class FeedSerializer(serializers.DocumentSerializer):
    #event = EventSerializer(read_only=True)
    id = drf_serializers.SerializerMethodField()
    geopoint = drf_serializers.SerializerMethodField()#GeoPointField()
    event_datetimes = drf_serializers.SerializerMethodField()

    # read only fields
    interests = drf_serializers.SerializerMethodField()# InterestChildSerializer(many=True, read_only=True)
    city = drf_serializers.SerializerMethodField() #CitySerializer(read_only=True)
    currency = drf_serializers.SerializerMethodField() #CurrencySerializer(read_only=True)
    author = drf_serializers.SerializerMethodField() #AuthorSerializer(read_only=True)

    rejection_reason = drf_serializers.SerializerMethodField()
    is_upvoted = drf_serializers.SerializerMethodField()
    is_in_favourites = drf_serializers.SerializerMethodField()
    images = drf_serializers.SerializerMethodField()
    #is_active = drf_serializers.BooleanField(read_only=True)

    title = drf_serializers.SerializerMethodField()
    description = drf_serializers.SerializerMethodField()
    language = drf_serializers.SerializerMethodField() # en ru fr it es de
    type = drf_serializers.SerializerMethodField()
    status = drf_serializers.SerializerMethodField()
    is_active = drf_serializers.SerializerMethodField()
    min_price = drf_serializers.SerializerMethodField()
    max_price = drf_serializers.SerializerMethodField()
    address = drf_serializers.SerializerMethodField()
    place_name = drf_serializers.SerializerMethodField()
    phones = drf_serializers.SerializerMethodField()#(drf_serializers.SerializerMethodField())
    email = drf_serializers.SerializerMethodField()
    web_site = drf_serializers.SerializerMethodField()
    votes_num = drf_serializers.SerializerMethodField()
    close_on_start = drf_serializers.SerializerMethodField()
    registration_link = drf_serializers.SerializerMethodField()
    tickets_link = drf_serializers.SerializerMethodField()
    min_age = drf_serializers.SerializerMethodField()
    max_age = drf_serializers.SerializerMethodField()

    # write only fields
    # interest_ids = drf_serializers.ListField(write_only=True, required=False)
    # currency_id = drf_serializers.SerializerMethodField() #serializers.ObjectIdField(write_only=True, required=False)
    # city_id = drf_serializers.SerializerMethodField() #serializers.ObjectIdField(write_only=True, required=False)
    # image_ids = drf_serializers.SerializerMethodField() #drf_serializers.ListField(write_only=True, required=False)
    datetimes = EventTimeSerializer(many=True, required=False)

    class Meta:
        model = Feed

    def get_id(self, obj):
        return str(obj['event']['id'])

    def get_title(self, obj):
        return obj['event']['title']

    def get_description(self, obj):
        return obj['event']['description']

    def get_language(self, obj):
        return obj['event']['language']

    def get_type(self, obj):
        return obj['event']['type']

    def get_status(self, obj):
        return obj['event']['status']

    def get_is_active(self, obj):
        return obj['event']['is_active']

    def get_min_price(self, obj):
        result = 0
        request = self.context.get("request")
        user_currency = request.user.settings.currency.code
        event_currency = obj['event']['currency'].code
        if user_currency == event_currency:
            return obj['event']['min_price']
        else:
            if obj['event']['min_price']:
                result = yahoo.exchange(source=event_currency,
                                target=user_currency,
                                amount=int(obj['event']['min_price']))
        return result

    def get_max_price(self, obj):
        result = 0
        request = self.context.get("request")
        user_currency = request.user.settings.currency.code
        event_currency = obj['event']['currency'].code
        if user_currency == event_currency:
            return obj['event']['max_price']
        else:
            if obj['event']['max_price']:
                result = yahoo.exchange(source=event_currency,
                                target=user_currency,
                                amount=int(obj['event']['max_price']))
        return result
        #return obj['event']['max_price']

    def get_address(self, obj):
        return obj['event']['address']

    def get_place_name(self, obj):
        return obj['event']['place_name']

    def get_phones(self, obj):
        return obj['event']['phones']

    def get_email(self, obj):
        return obj['event']['email']

    def get_votes(self, obj):
        return obj['event']['votes']

    def get_web_site(self, obj):
        return obj['event']['web_site']

    def get_votes_num(self, obj):
        return obj['event']['votes_num']

    def get_close_on_start(self, obj):
        return obj['event']['close_on_start']

    def get_registration_link(self, obj):
        return obj['event']['registration_link']

    def get_tickets_link(self, obj):
        return obj['event']['tickets_link']

    def get_min_age(self, obj):
        return obj['event']['min_age']

    def get_max_age(self, obj):
        return obj['event']['max_age']

    def get_geopoint(self, obj):
        return obj['event']['geopoint']

    def get_interests(self, obj):
        return InterestChildSerializer(obj['event']['interests'], many=True, read_only=True).data

    def get_city(self, obj):
        return CitySerializer(obj['event']['city'], read_only=True).data

    def get_currency(self, obj):
        request = self.context.get("request")
        user_currency = request.user.settings.currency
        return CurrencySerializer(user_currency, read_only=True).data

    def get_author(self, obj):
        return AuthorSerializer(obj['event']['author'], read_only=True).data

    def get_currency_id(self, obj):
        return serializers.ObjectIdField(obj['event']['currency'], required=False)

    def get_city_id(self, obj):
        return serializers.ObjectIdField(obj['event']['city'], required=False)

    def get_image_ids(self, obj):
        return drf_serializers.ListField(obj['event'].images, required=False)


    def get_is_upvoted(self, obj):
        if 'request' not in self.context:
            return False
        return bool(obj['event'].is_upvoted(self.context['request'].user))

    def get_is_in_favourites(self, obj):
        if 'request' not in self.context:
            return False
        return obj['event'].is_in_favourites(self.context['request'].user)

    def get_images(self, obj):
        return FileObjectSerializer(obj['event'].images, many=True).data

    # def get_datetimes(self, obj):
    #     #import pdb;pdb.set_trace()
    #     datetimes = []
    #     for item in obj['datetimes']:
    #         if string_to_date(str(item['date']), settings.DATE_STRING_FIELD_FORMAT) >= datetime.now().date():
    #             datetimes.append(item)
    #     return EventTimeSerializer(datetimes, many=True, required=False).data

    def get_event_datetimes(self, obj):
        datetimes = []
        for item in obj['event']['datetimes']:
            if string_to_date(str(item['date']), settings.DATE_STRING_FIELD_FORMAT) >= datetime.now().date():
                datetimes.append(item)
        return EventTimeSerializer(datetimes, many=True, required=False).data

    def get_rejection_reason(self, obj):
        if obj['event'].rejection_reasons.count() == 0:
            return None
        return RejectionReasonSerializer(obj['event'].rejection_reasons[0]).data


class EventAdminSerializer(LocalizedSerializer):

    # read only fields
    interests = InterestChildSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    rejection_reasons = RejectionReasonSerializer(many=True, read_only=True)
    images = drf_serializers.SerializerMethodField()
    datetimes = EventTimeSerializer(many=True, read_only=True)

    # write only fields
    interest_ids = drf_serializers.ListField(write_only=True, required=False)
    currency_id = serializers.ObjectIdField(write_only=True, required=False)
    city_id = serializers.ObjectIdField(write_only=True, required=False)
    image_ids = drf_serializers.CharField(write_only=True, required=False)
    geopoint_lng = drf_serializers.FloatField(write_only=True, required=False)
    geopoint_lat = drf_serializers.FloatField(write_only=True, required=False)
    raw_datetimes = drf_serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Event
        exclude = (
            'votes',
            'in_favourites',
        )

    def validate_city_id(self, value):
        try:
            city = City.objects.get(id=value)
        except City.DoesNotExist:
            raise ValidationError(_('No city with this city_id'))
        except City.MultipleObjectsReturned:
            raise ValidationError(_('Too many cities with this city_id'))
        return city

    def validate_currency_id(self, value):
        try:
            currency = Currency.objects.get(id=value)
        except Currency.DoesNotExist:
            raise ValidationError(_('No currency with this currency_id'))
        except Currency.MultipleObjectsReturned:
            raise ValidationError(_('Too many currencies with this currency_id'))
        return currency

    def validate(self, data):
        """
        Min_price should be less than Max_price.
        """
        if 'min_price' in data and 'max_price' in data and data['min_price'] > data['max_price']:
            raise ValidationError(_("Min_price should be less than Max_price"))
        return data

    def create(self, validated_data):
        city = validated_data.pop('city_id')
        currency = validated_data.pop('currency_id')
        interest_ids = validated_data.pop('interest_ids')
        image_ids = json.loads(validated_data.pop('image_ids')) if 'image_ids' in validated_data else []
        geopoint_lng = validated_data.pop('geopoint_lng') if 'geopoint_lng' in validated_data else None
        geopoint_lat = validated_data.pop('geopoint_lat') if 'geopoint_lat' in validated_data else None
        author = validated_data.pop('author')
        datetimes = validated_data.pop('raw_datetimes')
        event = super(EventAdminSerializer, self).create(validated_data)

        event.city = city
        event.currency = currency
        event.author = author
        if geopoint_lng and geopoint_lat:
            event.geopoint = (geopoint_lng, geopoint_lat, )
        event.interests = Interest.objects.filter(id__in=interest_ids)
        [event.datetimes.append(EventTime(**datetime)) for datetime in datetimes]
        event.save()

        map(lambda x: x.move_to_media(entity=event), FileObject.objects.filter(id__in=image_ids))
        #event.translate()
        event.create_feed()
        return event

    def update(self, instance, validated_data):
        datetimes = validated_data.pop('raw_datetimes') if 'raw_datetimes' in validated_data else None
        event = super(EventAdminSerializer, self).update(instance, validated_data)

        if datetimes:
            event.datetimes.delete()
            [event.datetimes.append(EventTime(**datetime)) for datetime in datetimes]
        if 'city_id' in validated_data:
            city = validated_data.pop('city_id')
            event.city = city
        if 'currency_id' in validated_data:
            currency = validated_data.pop('currency_id')
            event.currency = currency
        if 'interest_ids' in validated_data:
            interest_ids = validated_data.pop('interest_ids')
            event.interests = Interest.objects.filter(id__in=interest_ids)
        if 'image_ids' in validated_data:
            image_ids = set(json.loads(validated_data.pop('image_ids')))
            old_ids = set(map(lambda x: str(x.id), instance.images))
            FileObject.objects.filter(id__in=(old_ids-image_ids)).delete()
            map(lambda x: x.move_to_media(entity=event), FileObject.objects.filter(id__in=(image_ids-old_ids)))
        if 'geopoint_lng' in validated_data and 'geopoint_lat' in validated_data:
            geopoint_lng = validated_data.pop('geopoint_lng')
            geopoint_lat = validated_data.pop('geopoint_lat')
            event.geopoint = (geopoint_lng, geopoint_lat, )

        event.save()
        #event.translate()
        event.create_feed()
        return event

    def get_images(self, obj):
        return FileObjectSerializer(obj.images, many=True).data


class ComplaintSerializer(serializers.DocumentSerializer):
    author = AuthorSerializer(read_only=True)
    executor = AuthorSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Complaint
        exclude = (
            'date_edited',
        )


class FeedbackMessageSerializer(serializers.DocumentSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = FeedbackMessage
        exclude = (
            'date_edited',
        )

    def create(self, validated_data):
        author = validated_data.pop('author')
        fm = super(FeedbackMessageSerializer, self).create(validated_data)
        fm.author = author
        fm.save()
        return fm


class LogEntrySerializer(serializers.DocumentSerializer):
    author = AuthorSerializer()
    text = drf_serializers.CharField(read_only=True)

    class Meta:
        model = LogEntry
