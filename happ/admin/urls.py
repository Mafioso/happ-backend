from django.conf.urls import include, url

from django.views.generic import TemplateView
from . import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.IndexView.as_view(template_name='admin/index.html'), name="index"),
    url(r'^event/list/$', views.EventListView.as_view(template_name='admin/event_list.html'), name="event_list"),
    url(r'^city/list/$', views.CityListView.as_view(template_name='admin/cities_list.html'), name="city_list"),
]
