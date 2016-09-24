from django.conf.urls import include, url

from django.views.generic import TemplateView
from . import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.IndexView.as_view(template_name='admin/index.html'), name="index"),
    url(r'^login/$', views.IndexView.as_view(template_name='admin/login.html'), name="login"),
    url(r'^event/list/$', views.EventListView.as_view(template_name='admin/event_list.html'), name="event_list"),
    url(r'^city/list/$', views.CityListView.as_view(template_name='admin/cities_list.html'), name="city_list"),
    url(r'^category/list/$', views.CityListView.as_view(template_name='admin/categories_list.html'), name="category_list"),
    url(r'^interest/list/$', views.InterestListView.as_view(template_name='admin/interest_list.html'), name="interest_list"),
]
