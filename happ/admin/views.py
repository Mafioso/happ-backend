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

class LoginView(TemplateView):
    template_name = 'admin/login.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)

        return context


class EventListView(TemplateView):
    template_name = 'admin/event_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)

        return context

class CityListView(TemplateView):
    template_name = 'admin/cities_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(CityListView, self).get_context_data(**kwargs)

        return context

class CategoriesListView(TemplateView):
    template_name = 'admin/categories_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(CategoriesListView, self).get_context_data(**kwargs)

        return context

class InterestListView(TemplateView):
    template_name = 'admin/interest_list.html'

    def get_context_data(self, * args, ** kwargs):
        context = super(InterestListView, self).get_context_data(**kwargs)

        return context
