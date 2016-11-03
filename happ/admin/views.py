from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.views.generic import TemplateView

from ..models import User, Event, Interest
from .mixins import JWTAuthRequiredMixin


class LoginView(TemplateView):
    template_name = 'admin/login.html'


class DashboardView(JWTAuthRequiredMixin, TemplateView):
    template_name = 'admin/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        total_users = User.objects.count()
        total_users_lt = User.objects.filter(date_created__lte=datetime.now() - relativedelta(days=7)).count()
        context['total_users'] = total_users
        context['total_users_delta'] = (total_users - total_users_lt) / total_users * 100

        total_organizers = User.objects.filter(role=User.ORGANIZER).count()
        total_organizers_lt = User.objects.filter(role=User.ORGANIZER, date_created__lte=datetime.now() - relativedelta(days=7)).count()
        context['total_organizers'] = total_organizers
        context['total_organizers_delta'] = (total_organizers - total_organizers_lt) / 100

        total_events = Event.objects.count()
        total_events_lt = Event.objects.filter(date_created__lte=datetime.now() - relativedelta(days=7)).count()
        context['total_events'] = total_events
        context['total_events_delta'] = (total_events - total_events_lt) / total_events * 100

        total_interests = Interest.objects.count()
        total_interests_lt = Interest.objects.filter(date_created__lte=datetime.now() - relativedelta(days=7)).count()
        context['total_interests'] = total_interests
        context['total_interests_delta'] = (total_interests - total_interests_lt) / total_interests * 100

        context['by_age'] = (
            User.objects.filter(date_of_birth__ne=None).count(),
            User.objects.filter(date_of_birth__ne=None).filter(date_of_birth__gt=datetime.now() - relativedelta(years=18)).count(),
            User.objects.filter(date_of_birth__ne=None).filter(date_of_birth__lte=datetime.now() - relativedelta(years=18), date_of_birth__gt=datetime.now() - relativedelta(years=25)).count(),
            User.objects.filter(date_of_birth__ne=None).filter(date_of_birth__lte=datetime.now() - relativedelta(years=25), date_of_birth__gt=datetime.now() - relativedelta(years=50)).count(),
            User.objects.filter(date_of_birth__ne=None).filter(date_of_birth__lte=datetime.now() - relativedelta(years=50)).count(),
            User.objects.filter(date_of_birth=None).count(),
        )

        context['by_gender'] = (
            User.objects.filter(gender=User.MALE).count(),
            User.objects.filter(gender=User.FEMALE).count(),
        )

        context['last_events'] = Event.objects.order_by('-date_created')[:5]

        context['ads'] = {
            'total': Event.objects.filter(type=Event.FEATURED).count(),
            'moderation': Event.objects.filter(type=Event.FEATURED, status=Event.MODERATION).count(),
            'approved': Event.objects.filter(type=Event.FEATURED, status=Event.APPROVED).count(),
            'rejected': Event.objects.filter(type=Event.FEATURED, status=Event.REJECTED).count(),
        }

        return context


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
