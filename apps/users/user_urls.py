from django.urls import path

from apps.users.views import (
    UserDeactivateView,
    UserDetailView,
    UserListCreateView,
    UserReactivateView,
    UserResetPasswordView,
)

urlpatterns = [
    path("", UserListCreateView.as_view(), name="user_list_create"),
    path("<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user_deactivate"),
    path("<int:pk>/reactivate/", UserReactivateView.as_view(), name="user_reactivate"),
    path("<int:pk>/reset-password/", UserResetPasswordView.as_view(), name="user_reset_password"),
]
