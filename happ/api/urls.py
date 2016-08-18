from rest_framework_mongoengine.routers import DefaultRouter

from . import cities


router = DefaultRouter()
router.register(r'cities', cities.CityViewSet, 'cities')
