from django.contrib import auth

def get_user_model():
    from happ.models import User
    return User

auth.get_user_model = get_user_model
