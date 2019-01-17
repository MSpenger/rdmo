from __future__ import absolute_import

import json
import logging


from django.conf import settings
from django.contrib.auth.mixins import \
    PermissionRequiredMixin as DjangoPermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import translation
from django.views.generic.base import View

from rest_framework import mixins, viewsets
from rest_framework.response import Response

from rules.contrib.views import \
    PermissionRequiredMixin as RulesPermissionRequiredMixin

from .serializers import ChoicesSerializer
from .utils import get_next, get_referer, get_referer_path_info

log = logging.getLogger(__name__)


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('projects'))
    else:
        if settings.SHIBBOLETH:
            return render(request, 'core/home.html')
        elif settings.ACCOUNT or settings.SOCIALACCOUNT:
            from allauth.account.forms import LoginForm
            return render(request, 'core/home.html', {'form': LoginForm()})
        else:
            from django.contrib.auth.forms import AuthenticationForm
            return render(request, 'core/home.html', {'form': AuthenticationForm()})


def about(request):
    return render(request, 'core/about.html')


def i18n_switcher(request, language):
    referer = get_referer(request, default='/')

    # set the new language
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language

    return HttpResponseRedirect(referer)


def return_settings(request):
    data = {}
    data['default_uri_prefix'] = settings.DEFAULT_URI_PREFIX
    return HttpResponse(json.dumps(data), content_type='application/json')


class RedirectViewMixin(View):

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return HttpResponseRedirect(get_next(request))
        else:
            return super(RedirectViewMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(RedirectViewMixin, self).get_context_data(**kwargs)
        if 'next' in self.request.GET:
            context_data['next'] = self.request.GET['next']
        else:
            context_data['next'] = get_referer_path_info(self.request)
        return context_data

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']
        else:
            return super(RedirectViewMixin, self).get_success_url()


class PermissionRedirectMixin(object):

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise PermissionDenied(self.get_permission_denied_message())

        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())


class ModelPermissionMixin(PermissionRedirectMixin, DjangoPermissionRequiredMixin, object):
    pass


class ObjectPermissionMixin(PermissionRedirectMixin, RulesPermissionRequiredMixin, object):
    pass


class ChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ChoicesSerializer


class SettingsViewSet(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        return Response({
            'default_uri_prefix': settings.DEFAULT_URI_PREFIX
        })
