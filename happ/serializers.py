from rest_framework_mongoengine import serializers

from .models import City, Currency, User, UserSettings


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


class UserPayloadSerializer(serializers.DocumentSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
        )


class UserSerializer(serializers.DocumentSerializer):

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.settings = UserSettings()
        user.save()

        return user