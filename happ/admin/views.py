from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView, UpdateView, RedirectView
from django.core.urlresolvers import reverse

from .mixins import JWTAuthRequiredMixin


class IndexView(TemplateView):
    template_name = 'admin/index.html'
    #context_object_name = 'latest_question_list'

    def get_context_data(self, * args, ** kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
#        context['ran'] = range(1,19)

#        context['categories'] = models.Categories.objects.all()

        return context

class StatiscticView(TemplateView):
    template_name = 'statisctic.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(StatiscticView, self).get_context_data(**kwargs)

        return context

class LoginView(TemplateView):
    template_name = 'admin/login.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)

        return context


class EventListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/event_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)

        return context

class EventCreateView(TemplateView):
    template_name = 'admin/events/create.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)

        return context

class CityListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/cities_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(CityListView, self).get_context_data(**kwargs)

        return context

class CategoriesListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/categories_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(CategoriesListView, self).get_context_data(**kwargs)
        return context

class InterestListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/interest_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(InterestListView, self).get_context_data(**kwargs)

        return context

class UserListView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/users_list.html'
