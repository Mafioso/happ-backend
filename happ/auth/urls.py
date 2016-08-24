from django.conf.urls import url

from rest_framework_jwt.views import obtain_jwt_token

from .views import UserRegister, PasswordReset

urlpatterns = [
    url(r'login/$', obtain_jwt_token, name='login'),
    url(r'register/$', UserRegister.as_view(), name='register'),
    url(r'password/reset/$', PasswordReset.as_view(), name='password-reset'),
]
