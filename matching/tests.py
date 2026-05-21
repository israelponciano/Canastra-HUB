# matching/tests.py
from django.test import TestCase


class MatchingAppSmoke(TestCase):
    def test_app_installed(self):
        from django.apps import apps
        self.assertTrue(apps.is_installed("matching"))
