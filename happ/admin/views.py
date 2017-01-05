from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin

from ..models import User, Event, Interest, City, Currency, StaticText
from ..permissions import IsAdministrator, IsRoot
from .mixins import JWTAuthRequiredMixin, RoleMixin, StaticTextMixin


class LoginView(TemplateView):
    template_name = 'admin/login.html'


class DashboardView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
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

        context['top_liked'] = Event.objects.order_by('-votes_num')[:5]
        context['top_favourited'] = Event.objects.order_by('-in_favourites')[:5]

        return context


class EventListView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/event_list.html'

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True)
        context['interests'] = Interest.objects.filter(is_active=True, parent=None).order_by('title')
        return context


class EventModerationListView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/event_moderation_list.html'

    def get_context_data(self, **kwargs):
        context = super(EventModerationListView, self).get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True)
        context['interests'] = Interest.objects.filter(is_active=True, parent=None).order_by('title')
        return context


class EventCreateView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/events/create.html'

    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True)
        context['currencies'] = Currency.objects.all()
        context['interests'] = Interest.objects.filter(is_active=True, parent=None).order_by('title')
        return context


class EventEditView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/events/edit.html'

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['object'] = Event.objects.get(id=kwargs['id'])
        context['cities'] = City.objects.filter(is_active=True)
        context['currencies'] = Currency.objects.all()
        context['interests'] = Interest.objects.filter(is_active=True, parent=None)
        return context


class EventDetailView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/events/detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['api_key'] = settings.GOOGLE_API_KEY
        context['object'] = Event.objects.get(id=kwargs['id'])
        return context


class ProfileView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/profile/detail.html'


class ProfileEditView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/profile/edit.html'


class CityListView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/cities_list.html'


class CategoriesListView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/categories_list.html'


class InterestListView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/interest_list.html'


class UserListView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/users_list.html'


class OrganizersListView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/users_organizers.html'


class TermsOfServiceView(JWTAuthRequiredMixin, RoleMixin, StaticTextMixin, TemplateView):
    template_name = 'admin/settings/terms-of-service.html'
    type = StaticText.TERMS_OF_SERVICE


class PrivacyPolicyView(JWTAuthRequiredMixin, RoleMixin, StaticTextMixin, TemplateView):
    template_name = 'admin/settings/privacy-policy.html'
    type = StaticText.PRIVACY_POLICY


class FAQView(JWTAuthRequiredMixin, RoleMixin, StaticTextMixin, TemplateView):
    template_name = 'admin/settings/faq.html'
    type = StaticText.FAQ


class OrganizerRulesView(JWTAuthRequiredMixin, RoleMixin, StaticTextMixin, TemplateView):
    template_name = 'admin/settings/organizer-rules.html'
    type = StaticText.ORGANIZER_RULES


class ComplaintOpenView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/complaints_open_list.html'


class ComplaintClosedView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/complaints_closed_list.html'


class FeedbackView(JWTAuthRequiredMixin, RoleMixin, TemplateView):
    template_name = 'admin/feedback_list.html'


class ModeratorsListView(JWTAuthRequiredMixin, RoleMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/moderators_list.html'

    def test_func(self):
        return IsRoot().has_permission('', self.request, self) or \
               IsAdministrator().has_permission('', self.request, self)


class AdministratorsListView(JWTAuthRequiredMixin, RoleMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/administrators_list.html'

    def test_func(self):
        return IsRoot().has_permission('', self.request, self)
