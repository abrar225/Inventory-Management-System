"""Tests for UserService (role/group synchronization)."""

import pytest
from django.contrib.auth.models import Group

from apps.accounts.models import Role
from apps.accounts.services import UserService

from .factories import RoleFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestUserService:
    def test_create_user_assigns_role_and_group(self):
        role = RoleFactory(name=Role.Name.INVENTORY_MANAGER)
        user = UserService.create_user(
            email="im@example.com",
            password="pw123!",
            role=role,
        )
        assert user.role == role
        assert user.groups.filter(name=Role.Name.INVENTORY_MANAGER).exists()

    def test_assign_role_syncs_group_membership(self):
        old = RoleFactory(name=Role.Name.SALES_STAFF)
        new = RoleFactory(name=Role.Name.INVENTORY_MANAGER)
        user = UserFactory(role=old)
        UserService.assign_role(user, old)
        assert user.groups.filter(name=Role.Name.SALES_STAFF).exists()

        UserService.assign_role(user, new)
        # Old role-group dropped, new one added — exactly one role group.
        assert not user.groups.filter(name=Role.Name.SALES_STAFF).exists()
        assert user.groups.filter(name=Role.Name.INVENTORY_MANAGER).exists()
        role_groups = user.groups.filter(name__in=Role.Name.values)
        assert role_groups.count() == 1

    def test_deactivate_and_activate(self):
        user = UserFactory(is_active=True)
        UserService.deactivate_user(user)
        assert not user.is_active
        UserService.activate_user(user)
        assert user.is_active

    def test_set_password(self):
        user = UserFactory()
        UserService.set_password(user, "brand-new-pw-1!")
        user.refresh_from_db()
        assert user.check_password("brand-new-pw-1!")

    def test_assign_role_creates_group_if_missing(self):
        role = RoleFactory(name=Role.Name.SALES_STAFF)
        Group.objects.filter(name=Role.Name.SALES_STAFF).delete()
        user = UserFactory()
        UserService.assign_role(user, role)
        assert Group.objects.filter(name=Role.Name.SALES_STAFF).exists()
