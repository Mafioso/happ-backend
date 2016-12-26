from django.conf.urls import url

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from .views import (
    FacebookLogin,
    UserRegister,
    FacebookUserRegister,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    EmailConfirmationRequest,
    EmailConfirmation,
    AdminLogin,
)

urlpatterns = [
    url(r'admin/login/$', AdminLogin.as_view(), name='admin-login-api'),
    url(r'login/$', obtain_jwt_token, name='login'),
    url(r'login/facebook/$', FacebookLogin.as_view(), name='facebook-login'),
    url(r'refresh/$', refresh_jwt_token, name='refresh'),
    url(r'register/$', UserRegister.as_view(), name='register'),
    url(r'register/facebook/$', FacebookUserRegister.as_view(), name='facebook-register'),
    url(r'password/change/$', PasswordChange.as_view(), name='password-change'),
    url(r'password/reset/$', PasswordReset.as_view(), name='password-reset'),
    url(r'password/reset/confirm/$', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    url(r'email/confirm/request/$', EmailConfirmationRequest.as_view(), name='email-confirm-request'),
    url(r'email/confirm/$', EmailConfirmation.as_view(), name='email-confirm'),
]
