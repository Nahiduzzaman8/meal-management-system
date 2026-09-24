from django.contrib import admin
from django.urls import include, path

from apps.reports.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/users/", include("apps.users.user_urls")),
    path("api/months/", include("apps.months.urls")),
    path("api/meals/", include("apps.meals.urls")),
    path("api/guest-meals/", include("apps.guest_meals.urls")),
    path("api/deposits/", include("apps.deposits.urls")),
    path("api/expenses/", include("apps.expenses.urls")),
    path("api/adjustments/", include("apps.adjustments.urls")),
    path("api/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/reports/", include("apps.reports.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]
