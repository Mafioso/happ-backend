from django.conf.urls import include, url

from django.views.generic import TemplateView
from . import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^statisctic/$', views.StatiscticView.as_view(), name="statisctic"),
    url(r'^login/$', views.LoginView.as_view(), name="admin-login"),
    url(r'^event/list/$', views.EventListView.as_view(), name="event_list"),
    url(r'^event/create/$', views.EventCreateView.as_view(), name="event_create"),
    url(r'^city/list/$', views.CityListView.as_view(), name="city_list"),
    url(r'^category/list/$', views.CityListView.as_view(), name="category_list"),
    url(r'^interest/list/$', views.InterestListView.as_view(), name="interest_list"),
    url(r'^users/list/$', views.UserListView.as_view(), name="users_list"),
    url(r'^users/organizers/$', views.OrganizersListView.as_view(), name="users_organizers"),
]
