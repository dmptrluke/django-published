from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from published.utils import object_available

from ..constants import *
from .models import PublishedArticleTestModel


class GatekeeperArticleTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            username='gktest',
            email='test@test.com',
            password='1@3$5',
        )
        now = timezone.now()
        last_week = now - timedelta(days=7)
        earlier = now - timedelta(days=15)
        later = now + timedelta(days=7)
        wayback = now - timedelta(days=30)
        # Test cases
        # 2. Next week - NOT LIVE YET
        cls.a02 = PublishedArticleTestModel.objects.create(pk=2, title='Article Test 2', live_as_of=later,
                                                           publish_status=AVAILABLE_AFTER)

        # 3. Last week - IS LIVE
        cls.a03 = PublishedArticleTestModel.objects.create(pk=3, title='Article Test 3', live_as_of=last_week,
                                                           publish_status=AVAILABLE_AFTER)
        # 4. earlier + PERM LIVE
        cls.a04 = PublishedArticleTestModel.objects.create(pk=4, title='Article Test 4', live_as_of=earlier,
                                                           publish_status=AVAILABLE)
        # 5. wayback - but put offline
        cls.a05 = PublishedArticleTestModel.objects.create(pk=5, title='Article Test 5', live_as_of=wayback,
                                                           publish_status=NEVER_AVAILABLE)
        # 6. later - but PERM LIVE
        cls.a06 = PublishedArticleTestModel.objects.create(pk=6, title='Article Test 6', live_as_of=later,
                                                           publish_status=AVAILABLE)

    def setUp(self):
        self.client.login(username='gktest', password='1@3$5')

    # given the data before, only #3 and #4 are live to the public.
    #  to an admin, all but #5 are available
    def test_how_many_are_live_to_public(self):
        # based on the seed data above - the answer should be 2:
        n = 0
        articles = PublishedArticleTestModel.objects.all()
        for a in articles:
            if a.available_to_public:
                n += 1
        self.assertEqual(n, 3)
        print("Articles live: should get 3, and got ", n)

    def test_how_many_are_live_to_admin(self):
        # this should be 4 - you don't see anything that has publish_status = -1
        n = 0
        n_offline = 0
        articles = PublishedArticleTestModel.objects.all()
        for a in articles:
            if object_available(self.user, a):
                n += 1
            else:
                n_offline += 1
        self.assertEqual(n, 5)
        self.assertEqual(n_offline, 0)
        print("Articles available to admin (should be 5): ", n, ' Offline (should be 0): ', n_offline)

    def run_object_conditions(self, pk, label, expect):
        test = PublishedArticleTestModel.objects.get(pk=pk)
        print("%s: expect: %s, publish_status = %d, live_as_of = %s" % (
            label, expect, test.publish_status, test.live_as_of))
        result = object_available(None, test)
        return result

    def test_offline_is_not_live(self):
        """
        Permanently Offline --- publish_status = NEVER_AVAILABLE --- is not live.
        """
        self.assertFalse(self.run_object_conditions(5, 'Offline is not live', False))

    def test_future_is_not_live(self):
        """
        Staged for publish --- live_as_of > now --- is not live
        """
        self.assertFalse(self.run_object_conditions(2, 'Future is not live', False))

    def test_future_but_available_is_live(self):
        """
        Staged for publish --- live_as_of > now --- is not live
        """
        self.assertTrue(self.run_object_conditions(6, 'Perm Live but future is live', True))

    def test_perm_live_is_live(self):
        """
        Permanently live --- publish_status = AVAILABLE, live_as_of <= now --- is live
        """
        self.assertTrue(self.run_object_conditions(4, 'Perm Live is live', True))

    def test_past_set_is_live(self):
        """
        "live" --- publish_status != NEVER_AVAILABLE, live_as_of <= now --- is live
        """
        self.assertTrue(self.run_object_conditions(3, 'Past set is live', True))
