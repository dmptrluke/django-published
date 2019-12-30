from datetime import datetime

from django.db.models import Q

from published.models import PublishedAbstractModel


"""
 THIS IS THE MAIN GATEKEEPER

 This controls WHICH records show up on a website, based upon a set of rules.

 It returns True or False given:
    1. the requests.user object (which can be None)
    2. an object

 How this works:

    There are four possible publish states an object can be in.
        1. (publish_status =  1): Object is AVAILABLE - think of this as a ALWAYS ON switch
        2. (publish_status =  0): Object is CONDITIONALLY AVAILABLE - the "live_as_of" date is in the past
        3. (publish_status =  0): Object is PENDING AVAILABLE - the "live_as_of" date is still in the future
        5. (publish_status = -1): Object is ALWAYS UNAVAILABLE - this is the ALWAYS OFF Switch

 Page requesters can either be logged in to the Django Admin (i.e., staff) or not (i.e., the general public)

    RULE 1:   Objects ONLY EVER appear to the public (i.e., 'are live') if:
        a. The publish_status = 1 regardless of the live_as_of date
        b. The publish_status = 0 AND the live_as_of date exists and is in the past.

    RULE 2:   Objects with a publish_status of -1 don't appear on the site to the public.

    RULE 3:   Objects are shown on model listing pages to the public ONLY IF:
        a.  The object is "live" (see prior rules)
"""


def can_object_page_be_shown(user, this_object):
    # noinspection PyBroadException
    try:
        if user.is_staff:  # admin users can always see pages
            if this_object.publish_status >= 0 or this_object.treat_as_standalone == 1:
                return True  # I can see everything except specifically turned-off objects because I'm an admin
    except Exception:  # noqa: E722
        pass  # I am not logged in - continue

    if this_object.publish_status == PublishedAbstractModel.AVAILABLE:
        return True

    if not this_object:  # this object isn't live or doesn't exist
        return False

    if this_object.publish_status == PublishedAbstractModel.NEVER_AVAILABLE:
        return False

    if this_object.publish_status == PublishedAbstractModel.AVAILABLE_AFTER:
        if this_object.live_as_of is not None:
            now = datetime.now()
            delta = this_object.live_as_of <= now
            if not delta:
                return False
        else:
            # this should not happen, lets default to no access
            return False
        return True

    # this should not happen, lets default to no access
    return False


def can_object_page_be_shown_to_public(this_object):
    return can_object_page_be_shown(None, this_object)


def queryset_filter(qs, is_auth=False):
    """
    This is here because there are several places in other views that need to create partial querysets
    that are combined (e.g., on the Watch page, but also on the other episodic pages for things like "More from...").
    To make THAT work, you need to know which of those potentially associated objects are actually available on
    the site.

    This DOES take Administrative login into account (if is_auth == True), in which case the queryset is passed
    through unchecked.

    RAD - 2018-Aug-23
    """
    if not is_auth:
        # If you are not logged in, then live_as_of must exist (not None) and must be in the past.
        qs = qs.exclude(
            publish_status=PublishedAbstractModel.NEVER_AVAILABLE
        )
        qs = qs.exclude(
            Q(publish_status=PublishedAbstractModel.AVAILABLE_AFTER) &
            Q(live_as_of__gt=datetime.now())
        )
    return qs
