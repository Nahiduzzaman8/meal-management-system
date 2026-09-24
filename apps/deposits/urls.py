from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.deposits.views import DepositViewSet

router = DefaultRouter()
router.register(r"", DepositViewSet, basename="deposit")

urlpatterns = [
    path("", include(router.urls)),
]
