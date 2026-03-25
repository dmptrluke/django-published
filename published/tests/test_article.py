import pytest

from published.utils import object_available


@pytest.mark.django_db
class TestPublicAvailability:
    # NEVER_AVAILABLE is not visible to the public
    def test_offline_not_available(self, articles):
        assert not object_available(None, articles['offline'])

    # future AVAILABLE_AFTER is not yet visible
    def test_future_not_available(self, articles):
        assert not object_available(None, articles['future'])

    # past AVAILABLE_AFTER is visible
    def test_past_available(self, articles):
        assert object_available(None, articles['past'])

    # AVAILABLE is visible regardless of live_as_of
    def test_always_available(self, articles):
        assert object_available(None, articles['always'])

    # AVAILABLE with future live_as_of is still visible
    def test_always_future_available(self, articles):
        assert object_available(None, articles['always_future'])

    # three of five articles are publicly visible
    def test_public_count(self, articles):
        public = [a for a in articles.values() if a.available_to_public]
        assert len(public) == 3


@pytest.mark.django_db
class TestAdminAvailability:
    # superusers see all articles regardless of publish status
    def test_admin_sees_all(self, superuser, articles):
        visible = [a for a in articles.values() if object_available(superuser, a)]
        assert len(visible) == 5
