from rest_framework_mongoengine.routers import DefaultRouter

from . import cities, currencies, interests


router = DefaultRouter()
router.register(r'cities', cities.CityViewSet, 'cities')
router.register(r'currencies', currencies.CurrencyViewSet, 'currencies')
router.register(r'interests', interests.InterestViewSet, 'interests')
