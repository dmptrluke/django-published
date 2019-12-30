from django.core.exceptions import ValidationError
from django.db import models

from .utils import can_object_page_be_shown_to_pubilc

PUBLISH_STATUS_LIST = (
    (-1, 'Never Available'),
    (1, 'Available Now'),
    (0, 'Available after "Publish Date"'),
)


class PublishedAbstractModel(models.Model):
    NEVER_AVAILABLE = -1
    AVAILABLE_AFTER = 0
    AVAILABLE = 1

    PUBLISH_CHOICES = (
        (-1, 'Never Available'),
        (1, 'Available Now'),
        (0, 'Available after "Publish Date"'),
    )

    publish_status = models.IntegerField(
        'Publish',
        default=1, null=False,
        choices=PUBLISH_CHOICES
    )

    live_as_of = models.DateTimeField(
        'Publish Date',
        null=True, blank=True,
    )

    def clean(self):
        if (self.publish_status == self.AVAILABLE_AFTER) and (self.live_as_of is None):
            raise ValidationError({'publish_status': 'No date has been set!'})

    @property
    def available_to_public(self):
        """
        THIS IS ONLY TO BE USED IN TEMPLATES.
        It RELIES on the gatekeeper - so using it in front of the gatekeeper is counter-productive.
        """
        return can_object_page_be_shown_to_pubilc(self)

    class Meta:
        abstract = True
