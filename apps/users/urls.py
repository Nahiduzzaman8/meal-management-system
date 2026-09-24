from django.urls import path

from apps.users.views import (
    CustomTokenRefreshView,
    UserDeactivateView,
    UserDetailView,
    UserListCreateView,
    UserReactivateView,
    UserResetPasswordView,
    change_password_view,
    login_view,
    logout_view,
    me_view,
)

urlpatterns = [
    path("login/", login_view, name="auth_login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="auth_refresh"),
    path("logout/", logout_view, name="auth_logout"),
    path("me/", me_view, name="auth_me"),
    path("password/change/", change_password_view, name="auth_change_password"),
    path("users/", UserListCreateView.as_view(), name="user_list_create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user_deactivate"),
    path("users/<int:pk>/reactivate/", UserReactivateView.as_view(), name="user_reactivate"),
    path("users/<int:pk>/reset-password/", UserResetPasswordView.as_view(), name="user_reset_password"),
]
