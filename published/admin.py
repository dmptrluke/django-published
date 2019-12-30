from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe

from .constants import *


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
        if obj.publish_status == AVAILABLE:
            return mark_safe("<strong>Available</strong>")
        elif obj.publish_status == NEVER_AVAILABLE:
            return mark_safe("<strong>Never Available</strong>")
        else:  # AVAILABLE_AFTER
            if obj.live_as_of is None:
                return "N/A"
            else:

                if obj.live_as_of > timezone.now():
                    dstr = obj.live_as_of.strftime("%x")
                    return mark_safe(f"<strong>Available After: {dstr}</strong>")
                else:
                    return mark_safe("<strong>Available</strong>")

    show_publish_status.short_description = 'Current Status'

    class Meta:
        abstract = True


def add_to_readonly_fields():
    """
    This adds the django-published fields to the readonly_fields list.

    Usage (in your model admin):
        def get_readonly_fields(self, obj=None):
            return self.readonly_fields + gatekeeper_add_to_readonly_fields()
    """
    return ['show_publish_status']


def add_to_list_display():
    """
    This adds fields to list_display for the Admin changelist page for the model.
    """
    return ['show_publish_status']


def add_to_fieldsets(section=True, collapse=False):
    """
    Adds gatekeeper fields to your ModelAdmin fieldsets.
    Options:
        Section: you can add the fields either as it's own section or as part of a section.
        Collapse: whether the section should be collapsable or not.

    How to use:
        # section = False
        fieldsets = (
            (None, { 'fields': ( ('pk',), gatekeeper_add_to_fieldsets(section=False), ), }),
        )

        # section = True
        fieldsets = (
            (None, { 'fields': ( ('pk',), ), }),
            gatekeeper_add_to_fieldsets(section=True),
        )
    """

    fields = ('publish_status', 'show_publish_status', 'live_as_of')

    if section:
        if collapse:
            d = {'classes': ('collapse',), 'fields': fields, }
        else:
            d = {'fields': fields, }
        s = ('Gatekeeper', d)
        return s
    return fields
