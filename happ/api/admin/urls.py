from django.conf.urls import url

from rest_framework_mongoengine.routers import DefaultRouter

from . import countries, cities, currencies, interests, events, users, complaints, feedback, log
from . import UrlShortenerView


router = DefaultRouter()
router.register(r'countries', countries.CountryViewSet, 'admin-countries')
router.register(r'cities', cities.CityViewSet, 'admin-cities')
router.register(r'currencies', currencies.CurrencyViewSet, 'admin-currencies')
router.register(r'interests', interests.InterestViewSet, 'admin-interests')
router.register(r'events', events.EventViewSet, 'admin-events')
router.register(r'users', users.UserViewSet, 'admin-users')
router.register(r'complaints', complaints.ComplaintViewSet, 'admin-complaints')
router.register(r'feedback', feedback.FeedbackMessageViewSet, 'admin-feedback')
router.register(r'log', log.LogEntryViewSet, 'admin-log')

urlpatterns = [
    url(r'^shorten_url/$', UrlShortenerView.as_view(), name='admin-shorten-url'),
]

urlpatterns += router.urls
