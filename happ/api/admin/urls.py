from rest_framework_mongoengine.routers import DefaultRouter

from . import countries, cities, interests, events


router = DefaultRouter()
router.register(r'countries', countries.CountryViewSet, 'admin-countries')
router.register(r'cities', cities.CityViewSet, 'admin-cities')
router.register(r'interests', interests.InterestViewSet, 'admin-interests')
router.register(r'events', events.EventViewSet, 'events')
