from datetime import datetime

from django.contrib import admin
from django.utils.safestring import mark_safe

import pytz


def is_in_the_future(dt):
    """
    Is this (UTC) date/time value in the future or not?
    """
    if dt > datetime.now(pytz.utc):
        return True
    return False


class PublishedAdmin(admin.ModelAdmin):
    """
    This superclass incorporates the gatekeeper fields into the Django Admin.

    Because of the Python MRO, you can't put the typical ModelAdmin methods here, because
    if you have >1 abstract baseclasses to your ModelAdmin, the Python MRO will stop at the
    first instance of the method, e.g.:

        class Foo1(admin.ModelAdmin):
            def get_readonly_fields(self, obj=None):
                return self.readonly_fields + ('foo1_field')
        class Foo2(admin.ModelAdmin):
            def get_readonly_fields(self, obj=None):
                return self.readonly_fields + ('foo2_field')
        class MyModel(Foo1, Foo2):
            pass

    will stop at Foo1, and never get to Foo2.

    To get around this, there are "helper methods" in admin_helpers.py, you'll still have
    to create methods in your ModelAdmin classes using either PublishedAdmin or
    GatekeeperSerialAdmin but you can call these from there to get the desired behavior.
    """

    # Custom methods
    def show_publish_status(self, obj):
        """
        This creates an HTML string showing a object's gatekeeper status in a user-friendly way.
        """
        if obj.publish_status > 0:
            return mark_safe("<strong>Available</strong>")
        elif obj.publish_status < 0:
            return mark_safe("<strong>Never Available</strong>")
        else:  # it EQUALS zero
            if obj.live_as_of is None:
                return "N/A"
            else:

                if is_in_the_future(obj.live_as_of):
                    dstr = obj.live_as_of.strftime("%x")
                    return mark_safe(f"<b>Available After: {dstr}</b>")
                else:
                    return mark_safe("<strong>Available</strong>")

    show_publish_status.short_description = 'Current Status'

    class Meta:
        abstract = True
