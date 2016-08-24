from django.conf.urls import url

from rest_framework_jwt.views import obtain_jwt_token

from .views import UserRegister, PasswordReset, PasswordResetConfirm

urlpatterns = [
    url(r'login/$', obtain_jwt_token, name='login'),
    url(r'register/$', UserRegister.as_view(), name='register'),
    url(r'password/reset/$', PasswordReset.as_view(), name='password-reset'),
    url(r'password/reset/confirm/$', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
]
