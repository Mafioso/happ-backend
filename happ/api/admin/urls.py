from rest_framework_mongoengine.routers import DefaultRouter

from . import countries, cities, currencies, interests, events, users


router = DefaultRouter()
router.register(r'countries', countries.CountryViewSet, 'admin-countries')
router.register(r'cities', cities.CityViewSet, 'admin-cities')
router.register(r'currencies', currencies.CurrencyViewSet, 'admin-currencies')
router.register(r'interests', interests.InterestViewSet, 'admin-interests')
router.register(r'events', events.EventViewSet, 'admin-events')
router.register(r'users', users.UserViewSet, 'admin-users')
