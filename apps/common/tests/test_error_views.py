"""Tests for the custom error handler views and root redirect."""

import pytest
from django.test import RequestFactory
from django.urls import reverse

from apps.common import views

pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


class TestErrorHandlers:
    def test_handler403_status(self, rf):
        resp = views.handler403(rf.get("/x/"))
        assert resp.status_code == 403

    def test_handler404_status(self, rf):
        resp = views.handler404(rf.get("/x/"))
        assert resp.status_code == 404

    def test_handler500_status(self, rf):
        resp = views.handler500(rf.get("/x/"))
        assert resp.status_code == 500


class TestRootRedirect:
    def test_anonymous_root_redirects_to_login(self, client):
        # Middleware intercepts anonymous access before the home view.
        resp = client.get("/")
        assert resp.status_code == 302
        assert reverse("accounts:login") in resp.url
