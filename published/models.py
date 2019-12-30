from django.core.exceptions import ValidationError
from django.db import models

from .constants import *
from .utils import object_available_to_public


class PublishedAbstractModel(models.Model):
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
        if (self.publish_status == AVAILABLE_AFTER) and (self.live_as_of is None):
            raise ValidationError({'publish_status': 'No date has been set!'})

    @property
    def available_to_public(self):
        """
        THIS IS ONLY TO BE USED IN TEMPLATES.
        It RELIES on the gatekeeper - so using it in front of the gatekeeper is counter-productive.
        """
        return object_available_to_public(self)

    class Meta:
        abstract = True
