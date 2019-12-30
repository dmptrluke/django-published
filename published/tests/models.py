from django.db import models

from ..models import PublishedAbstractModel


class PublishedArticleTestModel(PublishedAbstractModel):
    title = models.CharField(max_length=100, null=False)
