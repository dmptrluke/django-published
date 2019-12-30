from datetime import datetime

import pytz


"""
 THIS IS THE MAIN GATEKEEPER

 This controls WHICH records show up on a website, based upon a set of rules.

 It returns True or False given:
    1. the requests.user object (which can be None)
    2. one of the PBSMM objects (Episode, Season, Site, Special)

 How this works:

    There are five possible publish states an object can be in.
        1. (publish_status =  1): Object is PERMANANTLY LIVE - think of this as a ALWAYS ON switch
        2. (publish_status =  0): Object is CONDITIONALLY LIVE - the "live_as_of" date is in the past
        3. (publish_status =  0): Object is PENDING LIVE - the "live_as_of" date is still in the future
        4. (publish_status =  0): Object is NOT YET PUBLISHED - the "live_as_of" date is NULL
        5. (publish_status = -1): Object is PERMANENTLY OFFLINE - this is the ALWAYS OFF Switch

 Page requesters can either be logged in to the Django Admin (i.e., staff) or not (i.e., the general public)

    RULE 1:   Objects - when created - start off with publish_status = 0 and live_as_of = None
        This means that the logged-in Admin user can edit the record and "see" the page for Q/A,
            but it is NOT AVAILABLE to the public.

    RULL 2:   Objects ONLY EVER appear to the public (i.e., 'are live') if:
        a. The publish_status = 1 regardless of the live_as_of date
        b. The publish_status = 0 AND the live_as_of date exists and is in the past.

    RULE 3:   Objects with a publish_status of -1 don't appear on the site to ANYONE.

    RULE 4:   Objects are shown on model listing pages to the public ONLY IF:
        a.  The object is "live" (see Rule 2)
        b.  Any PARENT objects ARE ALSO "live" (but see exception below)


STANDLONE OBJECTS:

    For objects with the treat_as_standalone field, and where that field == 1, the above rules apply
    EXCEPT FOR Rule 4b:   "standalone" objects do NOT CHECK their parents' publish states.

"""


def can_object_page_be_shown(user, this_object):
    """
    RAD: 4 Oct 2018 --- so a weird condition happened, and I'm not sure what the appropriate
        logic ought to be:

        If a STANDALONE Episode has a parental Show that has publish_status = -1, does the episode
        get blocked or not?

        On one hand, it should be YES, because if the entire SHOW is "permanently offline", then that
        logically should extend to their children.

        On the OTHER HAND, the entire point of "standalone" is "do NOT consult the parents", so it shouldn't
        MATTER what the

    """
    # noinspection PyBroadException
    try:
        if user.is_staff:  # admin users can always see pages
            if this_object.publish_status >= 0 or this_object.treat_as_standalone == 1:
                return True  # I can see everything except specifically turned-off objects because I'm an admin
    except Exception:  # noqa: E722
        pass  # I am not logged in - continue

    if this_object.publish_status == 1:  # this object is ALWAYS live
        return True

    if not this_object:  # this object isn't live or doesn't exist
        return False

    # THIS IS CORRECT: even if standaalone is "true" if publish is <0 then do not pass!
    if this_object.publish_status < 0:  # this object isn't live
        return False

    if this_object.publish_status == 0:  # this object MIGHT be live
        if this_object.live_as_of is not None:
            now = datetime.now(pytz.utc)
            delta = this_object.live_as_of <= now
            if not delta:
                return False
            # return this_object.live_as_of <= now # if I'm past my publish date it's LIVE, otherwise it's not live yet
        else:
            return False  # this object is still being working on - no publish date set yet.

    return True


def can_object_page_be_shown_to_pubilc(this_object):
    return can_object_page_be_shown(None, this_object)
