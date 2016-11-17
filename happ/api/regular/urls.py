from django.conf.urls import url

from rest_framework_mongoengine.routers import DefaultRouter

from . import cities, currencies, interests, events, users, languages
from . import TempUploadView, TermsOfServiceView, PrivacyPolicyView, OrganizerRulesView, GooglePlacesView


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
    url(r'^privacy-policy/$', PrivacyPolicyView.as_view(), name='privacy_policy_api'),
    url(r'^organizer-rules/$', OrganizerRulesView.as_view(), name='organizer_rules_api'),
    url(r'^places/$', GooglePlacesView.as_view(), name='places_api'),
]

urlpatterns += router.urls
