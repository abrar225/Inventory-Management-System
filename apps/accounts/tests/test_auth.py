"""Tests for authentication flows: login, logout, inactive lockout, reset."""

import pytest
from django.core import mail
from django.urls import reverse

from .factories import UserFactory

pytestmark = pytest.mark.django_db


class TestLogin:
    def test_login_page_renders(self, client):
        resp = client.get(reverse("accounts:login"))
        assert resp.status_code == 200
        assert b"Sign in" in resp.content

    def test_valid_login_redirects_to_dashboard(self, client):
        UserFactory(email="ok@example.com", password="pw123!")
        resp = client.post(
            reverse("accounts:login"),
            {"username": "ok@example.com", "password": "pw123!"},
        )
        assert resp.status_code == 302
        assert resp.url == reverse("dashboard:index")

    def test_invalid_password_stays_on_login(self, client):
        UserFactory(email="ok@example.com", password="pw123!")
        resp = client.post(
            reverse("accounts:login"),
            {"username": "ok@example.com", "password": "wrong"},
        )
        assert resp.status_code == 200
        assert b"Incorrect email or password." in resp.content

    def test_inactive_user_cannot_login(self, client):
        UserFactory(
            email="off@example.com", password="pw123!", is_active=False
        )
        resp = client.post(
            reverse("accounts:login"),
            {"username": "off@example.com", "password": "pw123!"},
        )
        assert resp.status_code == 200
        assert b"disabled" in resp.content

    def test_remember_me_unchecked_expires_at_browser_close(self, client):
        UserFactory(email="ok@example.com", password="pw123!")
        client.post(
            reverse("accounts:login"),
            {"username": "ok@example.com", "password": "pw123!"},
        )
        assert client.session.get_expire_at_browser_close()


class TestLogout:
    def test_logout_redirects_to_login(self, client):
        UserFactory(email="ok@example.com", password="pw123!")
        client.login(username="ok@example.com", password="pw123!")
        resp = client.post(reverse("accounts:logout"))
        assert resp.status_code == 302


class TestPasswordReset:
    def test_reset_sends_email(self, client):
        UserFactory(email="reset@example.com", password="pw123!")
        resp = client.post(
            reverse("accounts:password_reset"),
            {"email": "reset@example.com"},
        )
        assert resp.status_code == 302
        assert len(mail.outbox) == 1
        assert "reset@example.com" in mail.outbox[0].to

    def test_reset_unknown_email_still_redirects(self, client):
        # Must not reveal whether an account exists.
        resp = client.post(
            reverse("accounts:password_reset"),
            {"email": "nobody@example.com"},
        )
        assert resp.status_code == 302
        assert len(mail.outbox) == 0


class TestAuthenticationRequired:
    def test_anonymous_redirected_to_login(self, client):
        resp = client.get(reverse("dashboard:index"))
        assert resp.status_code == 302
        assert reverse("accounts:login") in resp.url

    def test_authenticated_can_reach_dashboard(self, client):
        UserFactory(email="ok@example.com", password="pw123!")
        client.login(username="ok@example.com", password="pw123!")
        resp = client.get(reverse("dashboard:index"))
        assert resp.status_code == 200

    def test_inactive_user_locked_out_mid_session(self, client):
        user = UserFactory(email="ok@example.com", password="pw123!")
        client.login(username="ok@example.com", password="pw123!")
        # Deactivate after login; middleware should force logout on next req.
        user.is_active = False
        user.save(update_fields=["is_active"])
        resp = client.get(reverse("dashboard:index"))
        assert resp.status_code == 302
