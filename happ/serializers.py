from rest_framework_mongoengine import serializers

from .models import City


class CitySerializer(serializers.DocumentSerializer):
    
    class Meta:
        model = City
