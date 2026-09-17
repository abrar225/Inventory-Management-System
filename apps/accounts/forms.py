"""Forms for authentication and profile management.

Server-side validation lives here; the schema requires validation at the form
layer for all user-facing forms. Styling is applied via widget CSS classes so
templates stay free of presentation logic beyond rendering the widgets.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)

from apps.accounts.models import Role

User = get_user_model()

# Shared Tailwind classes for text-like inputs (matches the design system:
# 48px height, 12px radius, blue focus).
_INPUT_CLASS = (
    "h-12 w-full rounded-xl border border-border bg-surface px-md "
    "text-body text-text-primary placeholder:text-text-secondary "
    "focus:border-primary focus:outline-none focus:ring-2 "
    "focus:ring-primary/30 dark:border-dark-border dark:bg-dark-surface "
    "dark:text-dark-text"
)


def _style(field: forms.Field, placeholder: str = "") -> None:
    """Apply the standard input styling to a form field's widget."""
    field.widget.attrs.setdefault("class", _INPUT_CLASS)
    if placeholder:
        field.widget.attrs.setdefault("placeholder", placeholder)


class EmailAuthenticationForm(AuthenticationForm):
    """Login form that authenticates by email.

    ``AuthenticationForm`` labels its identity field "username"; because our
    ``USERNAME_FIELD`` is email, the field already carries the email value —
    we only relabel it and switch to an email input for better UX and
    validation.
    """

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"autofocus": True, "autocomplete": "email"}
        ),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Incorrect email or password.",
        "inactive": "Your account has been disabled. "
        "Contact your administrator.",
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        _style(self.fields["username"], "you@example.com")
        _style(self.fields["password"], "••••••••")

    def confirm_login_allowed(self, user) -> None:
        """Reject inactive users with a clear message (App Flow §3)."""
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages["inactive"], code="inactive"
            )


class ProfileForm(forms.ModelForm):
    """Self-service profile edit (name, phone, avatar)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        _style(self.fields["first_name"], "First name")
        _style(self.fields["last_name"], "Last name")
        _style(self.fields["phone"], "Phone")
        # Avatar uses a file input; styling handled in the template component.


class StyledPasswordChangeForm(PasswordChangeForm):
    """Password change form with design-system styling."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for name in self.fields:
            _style(self.fields[name])


class StyledPasswordResetForm(PasswordResetForm):
    """Password reset request form with design-system styling."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        _style(self.fields["email"], "you@example.com")


class StyledSetPasswordForm(SetPasswordForm):
    """Set-new-password form (reset confirm) with design-system styling."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for name in self.fields:
            _style(self.fields[name])


class UserCreateForm(forms.ModelForm):
    """Admin form to register a new user in the system."""

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        empty_label="Select a Role",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Provide an initial account password.",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_active",
        ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Role  # local import to prevent cycles
        self.fields["role"].queryset = Role.objects.all()  # type: ignore[attr-defined]
        for name in self.fields:
            _style(self.fields[name])


class UserUpdateForm(forms.ModelForm):
    """Admin form to modify existing user credentials and permissions."""

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        empty_label="Select a Role",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        required=False,
        help_text="Leave blank to keep password unchanged.",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_active",
        ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Role  # local import to prevent cycles
        self.fields["role"].queryset = Role.objects.all()  # type: ignore[attr-defined]
        for name in self.fields:
            _style(self.fields[name])

