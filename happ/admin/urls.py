from django.conf.urls import include, url

from django.views.generic import TemplateView
from . import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.DashboardView.as_view(), name="dashboard"),
    url(r'^login/$', views.LoginView.as_view(), name="admin-login"),
    url(r'^event/list/$', views.EventListView.as_view(), name="event_list"),
    url(r'^event/moderation/$', views.EventModerationListView.as_view(), name="event_moderation_list"),
    url(r'^event/create/$', views.EventCreateView.as_view(), name="event_create"),
    url(r'^event/edit/(?P<id>[0-9a-z-]+)/$', views.EventEditView.as_view(), name="event_edit"),
    url(r'^event/(?P<id>[0-9a-z-]+)/$', views.EventDetailView.as_view(), name="event_detail"),
    url(r'^city/list/$', views.CityListView.as_view(), name="city_list"),
    url(r'^category/list/$', views.CategoriesListView.as_view(), name="category_list"),
    url(r'^interest/list/$', views.InterestListView.as_view(), name="interest_list"),
    url(r'^users/list/$', views.UserListView.as_view(), name="users_list"),
    url(r'^users/organizers/$', views.OrganizersListView.as_view(), name="users_organizers"),
    url(r'^settings/terms-of-service/$', views.TermsOfServiceView.as_view(), name="terms_of_service"),
    url(r'^settings/privacy-policy/$', views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    url(r'^settings/organizer-rules/$', views.OrganizerRulesView.as_view(), name="organizer_rules"),
]
