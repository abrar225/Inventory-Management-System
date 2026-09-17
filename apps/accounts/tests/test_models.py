"""Tests for the User and Role models."""

import uuid

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Role

from .factories import RoleFactory, UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_uuid_primary_key(self):
        user = UserFactory()
        assert isinstance(user.pk, uuid.UUID)

    def test_email_is_username_field(self):
        assert User.USERNAME_FIELD == "email"

    def test_str_prefers_full_name(self):
        user = UserFactory(first_name="Ada", last_name="Lovelace")
        assert str(user) == "Ada Lovelace"

    def test_str_falls_back_to_email(self):
        user = UserFactory(first_name="", last_name="")
        assert str(user) == user.email

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="x")

    def test_create_superuser_flags(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="pw"
        )
        assert admin.is_staff and admin.is_superuser

    def test_soft_delete_hides_from_default_manager(self):
        user = UserFactory()
        pk = user.pk
        user.delete()
        assert not User.objects.filter(pk=pk).exists()
        assert User.all_objects.filter(pk=pk).exists()

    def test_superuser_is_administrator(self):
        admin = User.objects.create_superuser(
            email="a@example.com", password="pw"
        )
        assert admin.is_administrator


class TestRoleModel:
    def test_role_str_uses_display_name(self):
        role = RoleFactory(name=Role.Name.INVENTORY_MANAGER)
        assert str(role) == "Inventory Manager"

    def test_role_property_reflects_assignment(self):
        role = RoleFactory(name=Role.Name.INVENTORY_MANAGER)
        user = UserFactory(role=role)
        assert user.is_inventory_manager
        assert user.role_name == Role.Name.INVENTORY_MANAGER
