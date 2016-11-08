from datetime import datetime

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers as drf_serializers
from rest_framework.exceptions import ValidationError
from rest_framework_mongoengine import serializers

from .models import Country, City, Currency, User, UserSettings, Interest, Event


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


class CountrySerializer(serializers.DocumentSerializer):

    class Meta:
        model = Country
        exclude = (
            'date_created',
            'date_edited',
        )


class CitySerializer(serializers.DocumentSerializer):
    # read only fields
    country_name = drf_serializers.CharField(read_only=True)

    # write only fields
    country_id = serializers.ObjectIdField(write_only=True)

    class Meta:
        model = City
        exclude = (
            'date_created',
            'date_edited',
            'country',
        )

    def create(self, validated_data):
        country_id = validated_data.pop('country_id')
        city = City.objects.create(**validated_data)
        country = Country.objects.get(id=country_id)
        city.country = country
        city.save()
        return city

    def update(self, instance, validated_data):
        country_id = validated_data.pop('country_id')
        city = super(CitySerializer, self).update(instance, validated_data)
        country = Country.objects.get(id=country_id)
        city.country = country
        city.save()
        return city


class CurrencySerializer(serializers.DocumentSerializer):

    class Meta:
        model = Currency
        exclude = (
            'date_created',
            'date_edited',
        )


class InterestSerializer(serializers.DocumentSerializer):
    # read only fields
    parent = serializers.ReferenceField(read_only=True)

    # write only fields
    is_global = drf_serializers.BooleanField(write_only=True)
    parent_id = serializers.ObjectIdField(write_only=True, allow_null=True)
    local_cities = drf_serializers.ListField(write_only=True)

    class Meta:
        model = Interest
        exclude = (
            'date_created',
            'date_edited',
        )

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id')
        local_cities = validated_data.pop('local_cities')
        interest = Interest.objects.create(**validated_data)
        if parent_id:
            parent = Interest.objects.get(id=parent_id)
            interest.parent = parent
        local_cities = City.objects.filter(id__in=local_cities)
        interest.local_cities = local_cities
        interest.save()
        return interest

    def update(self, instance, validated_data):
        parent_id = validated_data.pop('parent_id')
        local_cities = None
        if validated_data.get('local_cities') :
            local_cities = validated_data.pop('local_cities')
        interest = super(InterestSerializer, self).update(instance, validated_data)
        if parent_id:
            parent = Interest.objects.get(id=parent_id)
            interest.parent = parent
        if local_cities:
            local_cities = City.objects.filter(id__in=local_cities)
            interest.local_cities = local_cities
        interest.save()
        return interest


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

    class Meta:
        model = Interest
        exclude = (
            'date_created',
            'date_edited',
            'is_global',
            'local_cities',
        )


class UserSettingsSerializer(serializers.EmbeddedDocumentSerializer):

    class Meta:
        model = UserSettings


class UserSerializer(serializers.DocumentSerializer):
    # read only fields
    fn = drf_serializers.CharField(read_only=True)
    interests = InterestSerializer(source='current_interests', many=True, read_only=True)
    settings = UserSettingsSerializer(read_only=True)

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.settings = UserSettings()
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
        )


class EventSerializer(LocalizedSerializer):
    # read only fields
    interests = InterestChildSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    start_datetime = drf_serializers.CharField(read_only=True)
    end_datetime = drf_serializers.CharField(read_only=True)
    is_upvoted = drf_serializers.SerializerMethodField()
    is_in_favourites = drf_serializers.SerializerMethodField()

    # write only fields
    interest_ids = drf_serializers.ListField(write_only=True, required=False)
    currency_id = serializers.ObjectIdField(write_only=True, required=False)
    city_id = serializers.ObjectIdField(write_only=True, required=False)
    start_date = drf_serializers.DateField(write_only=True, required=False)
    start_time = drf_serializers.TimeField(write_only=True, required=False)
    end_date = drf_serializers.DateField(write_only=True, required=False)
    end_time = drf_serializers.TimeField(write_only=True, required=False)

    class Meta:
        model = Event
        extra_kwargs = {
            'city': {'read_only': True},
        }
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
        if datetime.combine(data['start_date'], data['start_time']) > datetime.combine(data['end_date'], data['end_time']):
            raise ValidationError(_("Start date should be earlier than End date"))
        return data

    def create(self, validated_data):
        city = validated_data.pop('city_id')
        currency = validated_data.pop('currency_id')
        interest_ids = validated_data.pop('interest_ids')
        author = validated_data.pop('author')
        event = super(EventSerializer, self).create(validated_data)

        event.city = city
        event.currency = currency
        event.author = author
        event.interests = Interest.objects.filter(id__in=interest_ids)
        event.save()
        # event.translate()
        return event

    def update(self, instance, validated_data):
        event = super(EventSerializer, self).update(instance, validated_data)

        if 'city_id' in validated_data:
            city = validated_data.pop('city_id')
            event.city = city
        if 'currency_id' in validated_data:
            currency = validated_data.pop('currency_id')
            event.currency = currency
        if 'interest_ids' in validated_data:
            interest_ids = validated_data.pop('interest_ids')
            event.interests = Interest.objects.filter(id__in=interest_ids)

        event.save()
        # event.translate()
        return event

    def get_is_upvoted(self, obj):
        if 'request' not in self.context:
            return False
        return bool(obj.is_upvoted(self.context['request'].user))

    def get_is_in_favourites(self, obj):
        if 'request' not in self.context:
            return False
        return obj.is_in_favourites(self.context['request'].user)
