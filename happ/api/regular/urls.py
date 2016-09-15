from rest_framework_mongoengine.routers import DefaultRouter

from . import cities, currencies, interests, events, users


router = DefaultRouter()
router.register(r'cities', cities.CityViewSet, 'cities')
router.register(r'currencies', currencies.CurrencyViewSet, 'currencies')
router.register(r'interests', interests.InterestViewSet, 'interests')
router.register(r'events', events.EventViewSet, 'events')
router.register(r'users', users.UsersViewSet, 'users')