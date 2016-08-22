from django.conf.urls import url

from rest_framework_mongoengine.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from . import cities, currencies


router = DefaultRouter()
router.register(r'cities', cities.CityViewSet, 'cities')
router.register(r'currencies', currencies.CurrencyViewSet, 'currencies')

urlpatterns = [
    url(r'auth/login/$', obtain_jwt_token, name='login'),
]