from django.db import models


class PublishStatus(models.IntegerChoices):
    NEVER_AVAILABLE = 0, 'Never Available'
    AVAILABLE = 1, 'Available'
    AVAILABLE_AFTER = 2, 'Available after "Publish Date"'


# backwards compat
NEVER_AVAILABLE = PublishStatus.NEVER_AVAILABLE
AVAILABLE = PublishStatus.AVAILABLE
AVAILABLE_AFTER = PublishStatus.AVAILABLE_AFTER
PUBLISH_CHOICES = PublishStatus.choices

__all__ = ['AVAILABLE', 'AVAILABLE_AFTER', 'NEVER_AVAILABLE', 'PUBLISH_CHOICES', 'PublishStatus']
