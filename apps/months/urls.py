from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.months.views import MonthViewSet

router = DefaultRouter()
router.register(r"", MonthViewSet, basename="month")

urlpatterns = [
    path("", include(router.urls)),
]
