"""Tests for role-based access control (decorators and mixin)."""

import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory
from django.views import View

from apps.accounts.decorators import RoleRequiredMixin, role_required
from apps.accounts.models import Role

from .factories import RoleFactory, UserFactory

pytestmark = pytest.mark.django_db


@role_required(Role.Name.ADMINISTRATOR)
def _admin_only_view(request):
    return HttpResponse("ok")


class _ManagerOnlyView(RoleRequiredMixin, View):
    allowed_roles = (Role.Name.INVENTORY_MANAGER,)

    def get(self, request):
        return HttpResponse("ok")


@pytest.fixture
def rf():
    return RequestFactory()


class TestRoleRequiredDecorator:
    def test_matching_role_allowed(self, rf):
        role = RoleFactory(name=Role.Name.ADMINISTRATOR)
        request = rf.get("/x/")
        request.user = UserFactory(role=role)
        assert _admin_only_view(request).status_code == 200

    def test_superuser_always_allowed(self, rf):
        request = rf.get("/x/")
        request.user = UserFactory(is_superuser=True)
        assert _admin_only_view(request).status_code == 200

    def test_wrong_role_denied(self, rf):
        role = RoleFactory(name=Role.Name.SALES_STAFF)
        request = rf.get("/x/")
        request.user = UserFactory(role=role)
        with pytest.raises(PermissionDenied):
            _admin_only_view(request)

    def test_anonymous_redirected(self, rf):
        from django.contrib.auth.models import AnonymousUser

        request = rf.get("/x/")
        request.user = AnonymousUser()
        resp = _admin_only_view(request)
        assert resp.status_code == 302


class TestRoleRequiredMixin:
    def test_matching_role_allowed(self, rf):
        role = RoleFactory(name=Role.Name.INVENTORY_MANAGER)
        request = rf.get("/x/")
        request.user = UserFactory(role=role)
        resp = _ManagerOnlyView.as_view()(request)
        assert resp.status_code == 200

    def test_wrong_role_denied(self, rf):
        role = RoleFactory(name=Role.Name.SALES_STAFF)
        request = rf.get("/x/")
        request.user = UserFactory(role=role)
        with pytest.raises(PermissionDenied):
            _ManagerOnlyView.as_view()(request)
