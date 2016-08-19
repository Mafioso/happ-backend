from rest_framework_mongoengine import serializers

from .models import City, Currency


class CitySerializer(serializers.DocumentSerializer):
    
    class Meta:
        model = City


class CurrencySerializer(serializers.DocumentSerializer):

    class Meta:
        model = Currency
        exclude = (
            'date_created',
            'date_edited',
        )
