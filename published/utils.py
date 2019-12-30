from django.db.models import Q
from django.utils import timezone

from .constants import *


"""
 THIS IS THE MAIN GATEKEEPER

 This controls WHICH records show up on a website, based upon a set of rules.

 It returns True or False given:
    1. the requests.user object (which can be None)
    2. an object

 How this works:

    There are four possible publish states an object can be in.
        1. (publish_status = AVAILABLE): Object is AVAILABLE - think of this as a ALWAYS ON switch
        2. (publish_status = AVAILABLE_AFTER): Object is CONDITIONALLY AVAILABLE - the "live_as_of" date is in the past
        3. (publish_status = AVAILABLE_AFTER): Object is PENDING AVAILABLE - the "live_as_of" date is in the future
        5. (publish_status = NEVER_AVAILABLE): Object is ALWAYS UNAVAILABLE - this is the ALWAYS OFF Switch

 Page requesters can either be logged in to the Django Admin (i.e., staff) or not (i.e., the general public)

    RULE 1:   Objects ONLY EVER appear to the public (i.e., 'are live') if:
        a. The publish_status = AVAILABLE regardless of the live_as_of date
        b. The publish_status = AVAILABLE_AFTER AND the live_as_of date exists and is in the past.

    RULE 2:   Objects with a publish_status of NEVER_AVAILABLE don't appear on the site to the public.

    RULE 3:   Objects are shown on model listing pages to the public ONLY IF:
          a.  The object is "live" (see prior rules)
"""


def object_available(user, this_object):
    if user is not None:
        if user.is_staff:
            # admin users can always see everything
            return True

    if this_object.publish_status == AVAILABLE:
        return True

    if not this_object:  # this object isn't live or doesn't exist
        return False

    if this_object.publish_status == NEVER_AVAILABLE:
        return False

    if this_object.publish_status == AVAILABLE_AFTER:
        if this_object.live_as_of is not None:
            now = timezone.now()
            delta = this_object.live_as_of <= now
            if not delta:
                return False
        else:
            # this should not happen, default to no access
            return False
        return True

    # this should not happen, default to no access
    return False


def object_available_to_public(this_object):
    return object_available(None, this_object)


def queryset_filter(qs, user=None):
    """
    This is here because there are several places in other views that need to create partial querysets
    that are combined (e.g., on the Watch page, but also on the other episodic pages for things like "More from...").
    To make THAT work, you need to know which of those potentially associated objects are actually available on
    the site.

    This DOES take Administrative login into account (if is_auth == True), in which case the queryset is passed
    through unchecked.

    RAD - 2018-Aug-23
    """
    # if a user is provided, we run admin checks
    if user is not None:
        if user.is_staff:
            return qs

    qs = qs.exclude(
        publish_status=NEVER_AVAILABLE
    )
    qs = qs.exclude(
        Q(publish_status=AVAILABLE_AFTER) & Q(live_as_of__gt=timezone.now())
    )
    return qs
