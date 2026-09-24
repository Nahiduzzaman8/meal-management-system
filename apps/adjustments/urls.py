from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.adjustments.views import AdjustmentViewSet

router = DefaultRouter()
router.register(r"", AdjustmentViewSet, basename="adjustment")

urlpatterns = [
    path("", include(router.urls)),
]
