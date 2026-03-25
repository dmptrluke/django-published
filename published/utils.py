from django.db.models import Q
from django.utils import timezone

from .constants import PublishStatus


def object_available(user, this_object):
    """Return True if the object should be visible to the given user (or the public if None)."""
    if user is not None and user.is_staff:
        return True

    if this_object.publish_status == PublishStatus.AVAILABLE:
        return True

    if not this_object:
        return False

    if this_object.publish_status == PublishStatus.NEVER_AVAILABLE:
        return False

    if this_object.publish_status == PublishStatus.AVAILABLE_AFTER:
        if this_object.live_as_of is not None and this_object.live_as_of <= timezone.now():
            return True
        return False

    return False


def object_available_to_public(this_object):
    return object_available(None, this_object)


def queryset_filter(qs, user=None):
    """Filter a queryset to only include publicly available objects. Staff see everything."""
    if user is not None and user.is_staff:
        return qs

    qs = qs.exclude(publish_status=PublishStatus.NEVER_AVAILABLE)
    qs = qs.exclude(Q(publish_status=PublishStatus.AVAILABLE_AFTER) & Q(live_as_of__gt=timezone.now()))
    return qs
