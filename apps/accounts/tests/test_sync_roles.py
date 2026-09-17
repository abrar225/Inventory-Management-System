"""Tests for the sync_roles management command."""

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command

from apps.accounts.models import Role

pytestmark = pytest.mark.django_db


class TestSyncRoles:
    def test_creates_roles_and_groups(self):
        call_command("sync_roles")
        for name, _ in Role.Name.choices:
            assert Role.objects.filter(name=name).exists()
            assert Group.objects.filter(name=name).exists()

    def test_administrator_gets_all_permissions(self):
        call_command("sync_roles")
        admin_group = Group.objects.get(name=Role.Name.ADMINISTRATOR)
        assert admin_group.permissions.count() == Permission.objects.count()

    def test_is_idempotent(self):
        call_command("sync_roles")
        call_command("sync_roles")
        # Exactly three roles/groups — no duplicates on re-run.
        assert Role.objects.filter(name__in=Role.Name.values).count() == 3
