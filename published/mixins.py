from django.db.models import Q
from django.http import Http404
from django.utils import timezone

from .constants import *
from .utils import object_available


class PublishedListMixin:
    """
    This is for Listing views that apply to all object ListView classes.
    """

    def get_queryset(self):
        qs = super().get_queryset()

        # If you're logged in you can see everything
        if not self.request.user.is_authenticated:
            qs = qs.exclude(
                publish_status=NEVER_AVAILABLE
            )
            qs = qs.exclude(
                Q(publish_status=AVAILABLE_AFTER) & Q(live_as_of__gt=timezone.now())
            )
        return qs


class PublishedDetailMixin:
    """
    This is for detail views that apply to all object DetailView classes.

    WE CANNOT USE the "available_to_public" property as a quick, "simple" workaround because you have to be able
    to reliably send the self.request.user to the gatekeeper (available_to_public is really only supposed
    to be used as a test within TEMPLATES, i.e., AFTER the gatekeeper has done its job!)
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if object_available(self.request.user, obj):
            return obj

        raise Http404()
