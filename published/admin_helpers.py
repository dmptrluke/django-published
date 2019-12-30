BASIC_FIELDS = (('publish_status', 'show_publish_status', 'live_as_of',))

GATEKEEPER_ACTIONS = [
    'gatekeeper_set_to_default',
    'gatekeeper_permanently_online',
    'gatekeeper_take_online_now',
    'gatekeeper_conditionally_online',
    'gatekeeper_take_offline',
]


def add_to_readonly_fields():
    """
    This adds the gatekeeper fields to the readonly_fields list.

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

    fields = BASIC_FIELDS

    if section:
        if collapse:
            d = {'classes': ('collapse',), 'fields': fields, }
        else:
            d = {'fields': fields, }
        s = ('Gatekeeper', d)
        return s
    return fields
