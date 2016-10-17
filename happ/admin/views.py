from django.views.generic import TemplateView

from .mixins import JWTAuthRequiredMixin


class IndexView(TemplateView):
    template_name = 'admin/index.html'


class StatiscticView(TemplateView):
    template_name = 'statisctic.html'


class LoginView(TemplateView):
    template_name = 'admin/login.html'


class EventListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/event_list.html'


class EventModerationListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/event_moderation_list.html'


class EventCreateView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/events/create.html'


class CityListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/cities_list.html'


class CategoriesListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/categories_list.html'


class InterestListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/interest_list.html'


class UserListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/users_list.html'


class OrganizersListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/users_organizers.html'
