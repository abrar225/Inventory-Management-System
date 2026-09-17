"""Test factories for the accounts app."""

import factory
from django.contrib.auth import get_user_model

from apps.accounts.models import Role

User = get_user_model()


class RoleFactory(factory.django.DjangoModelFactory):
    """Factory for Role rows (uses get_or_create — roles are a fixed set)."""

    class Meta:
        model = Role
        django_get_or_create = ("name",)

    name = Role.Name.SALES_STAFF


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for users. Password defaults to 'password123!'."""

    class Meta:
        model = User
        django_get_or_create = ("email",)
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.LazyAttribute(lambda o: o.email)
    first_name = "Test"
    last_name = "User"
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password(extracted or "password123!")
        self.save()
