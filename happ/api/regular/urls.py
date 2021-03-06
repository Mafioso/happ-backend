from django.conf.urls import url

from rest_framework_mongoengine.routers import DefaultRouter

from . import cities, currencies, interests, events, users, languages, complaints, feedback
from . import (
    VersionView,
    TempUploadView,
    TermsOfServiceView,
    PrivacyPolicyView,
    OrganizerRulesView,
    FAQView,
    GooglePlacesView,
    GooglePhotosView,
    YahooExchangeView,
    AppRedirectView,
)


router = DefaultRouter()
router.register(r'cities', cities.CityViewSet, 'cities')
router.register(r'currencies', currencies.CurrencyViewSet, 'currencies')
router.register(r'interests', interests.InterestViewSet, 'interests')
router.register(r'events', events.EventViewSet, 'events')
router.register(r'users', users.UsersViewSet, 'users')
router.register(r'languages', languages.LanguageViewSet, 'languages')
router.register(r'complaints', complaints.ComplaintViewSet, 'complaints')
router.register(r'feedback', feedback.FeedbackMessageViewSet, 'feedback')

urlpatterns = [
    url(r'^version/$', VersionView.as_view(), name='version_api'),
    url(r'^upload/$', TempUploadView.as_view(), name='temp-upload-url'),
    url(r'^terms-of-service/$', TermsOfServiceView.as_view(), name='terms_of_service_api'),
    url(r'^privacy-policy/$', PrivacyPolicyView.as_view(), name='privacy_policy_api'),
    url(r'^organizer-rules/$', OrganizerRulesView.as_view(), name='organizer_rules_api'),
    url(r'^faq/$', FAQView.as_view(), name='faq_api'),
    url(r'^places/$', GooglePlacesView.as_view(), name='google_places_api'),
    url(r'^photos/$', GooglePhotosView.as_view(), name='google_photos_api'),
    url(r'^exchange/$', YahooExchangeView.as_view(), name='yahoo_exchange_api'),
    url(r'^redirect/$', AppRedirectView.as_view(), name='redirect'),
]

urlpatterns += router.urls
