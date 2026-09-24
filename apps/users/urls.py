from django.urls import path

from apps.users.views import CustomTokenRefreshView, change_password_view, login_view, logout_view, me_view

urlpatterns = [
    path("login/", login_view, name="auth_login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="auth_refresh"),
    path("logout/", logout_view, name="auth_logout"),
    path("me/", me_view, name="auth_me"),
    path("password/change/", change_password_view, name="auth_change_password"),
]
