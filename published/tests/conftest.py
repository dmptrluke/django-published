from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

import pytest

from published.constants import PublishStatus
from published.tests.models import PublishedArticleTestModel


@pytest.fixture()
def superuser(db):
    return User.objects.create_superuser(
        username='gktest',
        email='test@test.com',
        password='1@3$5',
    )


@pytest.fixture()
def articles(db):
    now = timezone.now()
    return {
        'future': PublishedArticleTestModel.objects.create(
            title='Future',
            live_as_of=now + timedelta(days=7),
            publish_status=PublishStatus.AVAILABLE_AFTER,
        ),
        'past': PublishedArticleTestModel.objects.create(
            title='Past',
            live_as_of=now - timedelta(days=7),
            publish_status=PublishStatus.AVAILABLE_AFTER,
        ),
        'always': PublishedArticleTestModel.objects.create(
            title='Always',
            live_as_of=now - timedelta(days=15),
            publish_status=PublishStatus.AVAILABLE,
        ),
        'offline': PublishedArticleTestModel.objects.create(
            title='Offline',
            live_as_of=now - timedelta(days=30),
            publish_status=PublishStatus.NEVER_AVAILABLE,
        ),
        'always_future': PublishedArticleTestModel.objects.create(
            title='Always Future',
            live_as_of=now + timedelta(days=7),
            publish_status=PublishStatus.AVAILABLE,
        ),
    }
