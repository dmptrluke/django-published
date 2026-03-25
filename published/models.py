from django.core.exceptions import ValidationError
from django.db import models

from .constants import PublishStatus
from .utils import object_available_to_public


class PublishedModel(models.Model):
    publish_status = models.SmallIntegerField(
        'Publish',
        default=PublishStatus.AVAILABLE,
        null=False,
        choices=PublishStatus.choices,
    )

    live_as_of = models.DateTimeField(
        'Publish Date',
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def clean(self):
        if (self.publish_status == PublishStatus.AVAILABLE_AFTER) and (self.live_as_of is None):
            raise ValidationError({'publish_status': 'No date has been set!'})

    @property
    def available_to_public(self):
        """
        THIS IS ONLY TO BE USED IN TEMPLATES.
        It RELIES on the gatekeeper - so using it in front of the gatekeeper is counter-productive.
        """
        return object_available_to_public(self)


# backwards compatability
PublishedAbstractModel = PublishedModel
