from django.conf.urls import include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.DashboardView.as_view(), name="dashboard"),
    url(r'^login/$', views.LoginView.as_view(), name="admin-login"),
    url(r'^profile/$', views.ProfileView.as_view(), name="admin-profile"),
    url(r'^profile/edit/$', views.ProfileEditView.as_view(), name="admin-profile-edit"),
    url(r'^events/$', views.EventListView.as_view(), name="event_list"),
    url(r'^events/moderation/$', views.EventModerationListView.as_view(), name="event_moderation_list"),
    url(r'^events/create/$', views.EventCreateView.as_view(), name="event_create"),
    url(r'^events/edit/(?P<id>[0-9a-z-]+)/$', views.EventEditView.as_view(), name="event_edit"),
    url(r'^events/(?P<id>[0-9a-z-]+)/$', views.EventDetailView.as_view(), name="event_detail"),
    url(r'^cities/$', views.CityListView.as_view(), name="city_list"),
    url(r'^categories/$', views.CategoriesListView.as_view(), name="category_list"),
    url(r'^interests/$', views.InterestListView.as_view(), name="interest_list"),
    url(r'^users/$', views.UserListView.as_view(), name="users_list"),
    url(r'^users/organizers/$', views.OrganizersListView.as_view(), name="users_organizers"),
    url(r'^settings/terms-of-service/$', views.TermsOfServiceView.as_view(), name="terms_of_service"),
    url(r'^settings/privacy-policy/$', views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    url(r'^settings/organizer-rules/$', views.OrganizerRulesView.as_view(), name="organizer_rules"),
    url(r'^settings/faq/$', views.FAQView.as_view(), name="faq"),
    url(r'^complaints/open/$', views.ComplaintOpenView.as_view(), name="complaints_open"),
    url(r'^complaints/closed/$', views.ComplaintClosedView.as_view(), name="complaints_closed"),
    url(r'^feedback/$', views.FeedbackView.as_view(), name="feedback"),
    url(r'^moderators/$', views.ModeratorsListView.as_view(), name="moderators_list"),
    url(r'^administrators/$', views.AdministratorsListView.as_view(), name="administrators_list"),
]
