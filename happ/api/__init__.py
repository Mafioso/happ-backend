from django.contrib import auth

from happ.models import User


def get_user_model():
    return User

auth.get_user_model = get_user_model
