"""URL patterns for authentication and profile management.

The ``accounts`` namespace and URL names here must match the exempt route
names declared in settings (``LOGIN_EXEMPT_URL_NAMES``).
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # Profile & password change (authenticated)
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/password/",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "profile/password/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    # Password reset flow
    path(
        "password-reset/",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/sent/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # User Management (Administrator only)
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/add/", views.UserCreateView.as_view(), name="user_add"),
    path("users/<uuid:pk>/", views.UserUpdateView.as_view(), name="user_update"),
]
