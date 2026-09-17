"""Authentication and profile views.

Built on Django's class-based auth views, wired to the styled forms and the
``accounts`` template set. Business logic (role/group changes) is not handled
here — that belongs to ``UserService`` and arrives with user management in a
later phase. These views cover the self-service auth flows from App Flow §3
and §15.
"""

import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .decorators import RoleRequiredMixin
from .forms import (
    EmailAuthenticationForm,
    ProfileForm,
    StyledPasswordChangeForm,
    StyledPasswordResetForm,
    StyledSetPasswordForm,
    UserCreateForm,
    UserUpdateForm,
)
from .models import Role
from .services import UserService

logger = logging.getLogger("ims")

User = get_user_model()


class LoginView(auth_views.LoginView):
    """Email/password login (App Flow §3).

    Honors a "Remember me" checkbox: when unchecked, the session expires when
    the browser closes; when checked, Django's configured session age applies.
    """

    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember = self.request.POST.get("remember_me")
        # Expire at browser close unless "remember me" was ticked.
        self.request.session.set_expiry(0 if not remember else None)
        logger.info("Login success: %s", form.get_user().email)
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    """Log out and return to the login page."""


class ProfileView(LoginRequiredMixin, UpdateView):
    """View and edit the current user's own profile (App Flow §15)."""

    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)


class PasswordChangeView(auth_views.PasswordChangeView):
    """Change own password while authenticated."""

    template_name = "accounts/password_change.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("accounts:password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


# --- Password reset flow (App Flow §3) -------------------------------------
class PasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/emails/password_reset_email.txt"
    subject_template_name = "accounts/emails/password_reset_subject.txt"
    form_class = StyledPasswordResetForm
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class UserListView(RoleRequiredMixin, ListView):
    """Admin-only panel to list all active users and their system roles."""

    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    allowed_roles = [Role.Name.ADMINISTRATOR]

    def get_queryset(self):
        return User.objects.filter(is_deleted=False).select_related("role").order_by("email")


class UserCreateView(RoleRequiredMixin, CreateView):
    """Admin-only view to create a new user and assign roles atomically."""

    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    allowed_roles = [Role.Name.ADMINISTRATOR]

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        role = form.cleaned_data["role"]
        is_active = form.cleaned_data["is_active"]

        creator = self.request.user
        assert not creator.is_anonymous

        try:
            user = UserService.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=is_active,
                created_by=creator,
            )
            # Add optional fields not covered by create_user constructor
            user.username = form.cleaned_data.get("username", "")
            user.phone = form.cleaned_data.get("phone", "")
            user.save(update_fields=["username", "phone"])

            messages.success(
                self.request, f"User account {user.email} created successfully."
            )
            return redirect("accounts:user_list")
        except Exception as e:
            form.add_error(None, f"Error creating user: {str(e)}")
            return self.form_invalid(form)


class UserUpdateView(RoleRequiredMixin, UpdateView):
    """Admin-only view to edit an existing user's profile and assign roles."""

    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    allowed_roles = [Role.Name.ADMINISTRATOR]

    def get_queryset(self):
        return User.objects.filter(is_deleted=False)

    def form_valid(self, form):
        updater = self.request.user
        assert not updater.is_anonymous

        try:
            user = form.save(commit=False)
            role = form.cleaned_data["role"]
            password = form.cleaned_data.get("password")

            # Sync role and Django Group assignment
            UserService.assign_role(user, role, changed_by=updater)

            if password:
                UserService.set_password(user, password, changed_by=updater)

            user.save()
            messages.success(
                self.request, f"User account {user.email} updated successfully."
            )
            return redirect("accounts:user_list")
        except Exception as e:
            form.add_error(None, f"Error updating user: {str(e)}")
            return self.form_invalid(form)

