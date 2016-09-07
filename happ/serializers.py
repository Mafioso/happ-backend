from datetime import datetime

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers as drf_serializers
from rest_framework.exceptions import ValidationError
from rest_framework_mongoengine import serializers

from .models import City, Currency, User, UserSettings, Interest, Event


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


class CitySerializer(serializers.DocumentSerializer):
    country_name = drf_serializers.CharField()

    class Meta:
        model = City
        exclude = (
            'date_created',
            'date_edited',
            'country',
        )


class CurrencySerializer(serializers.DocumentSerializer):

    class Meta:
        model = Currency
        exclude = (
            'date_created',
            'date_edited',
        )


class InterestSerializer(serializers.DocumentSerializer):

    class Meta:
        model = Interest
        exclude = (
            'date_created',
            'date_edited',
            'is_global',
            'local_cities',
        )


class InterestChildSerializer(serializers.DocumentSerializer):
    parent = InterestSerializer()

    class Meta:
        model = Interest
        exclude = (
            'date_created',
            'date_edited',
            'is_global',
            'local_cities',
        )

class InterestParentSerializer(serializers.DocumentSerializer):
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
    interests = InterestSerializer(many=True, read_only=True)
    settings = UserSettingsSerializer(read_only=True)

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True}
        }
        exclude = (
            'favorites',
        )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
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
    interests = InterestChildSerializer(many=True, required=False)
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.ObjectIdField(write_only=True)
    city = serializers.ObjectIdField(read_only=True)
    city_id = serializers.ObjectIdField(write_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Event
        extra_kwargs = {
            'start_date': {'write_only': True},
            'start_time': {'write_only': True},
            'end_date': {'write_only': True},
            'end_time': {'write_only': True},
            'start_datetime': {'read_only': True},
            'end_datetime': {'read_only': True},
        }

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
        if data['start_date'] + data['start_time'] > data['end_date'] + data['end_time']:
            raise ValidationError(_("Start date should be earlier than End date"))
        return data

    def create(self, validated_data):
        city = validated_data.pop('city_id')
        currency = validated_data.pop('currency_id')
        author = validated_data.pop('author')
        event = super(EventSerializer, self).create(validated_data)

        event.city = city
        event.currency = currency
        event.author
        event.save()
        event.translate()
        return event

    def update(self, instance, validated_data):
        event = super(EventSerializer, self).update(instance, validated_data)
        event.translate()
        return event
