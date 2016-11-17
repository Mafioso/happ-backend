from django.conf.urls import url

from rest_framework_mongoengine.routers import DefaultRouter

from . import cities, currencies, interests, events, users, languages
from . import TempUploadView, TermsOfServiceView


router = DefaultRouter()
router.register(r'cities', cities.CityViewSet, 'cities')
router.register(r'currencies', currencies.CurrencyViewSet, 'currencies')
router.register(r'interests', interests.InterestViewSet, 'interests')
router.register(r'events', events.EventViewSet, 'events')
router.register(r'users', users.UsersViewSet, 'users')
router.register(r'languages', languages.LanguageViewSet, 'languages')

urlpatterns = [
    url(r'^upload/$', TempUploadView.as_view(), name='temp-upload-url'),
    url(r'^terms-of-service/$', TermsOfServiceView.as_view(), name='terms_of_service_api'),
]

urlpatterns += router.urls
