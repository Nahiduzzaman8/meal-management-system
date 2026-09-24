from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.guest_meals.views import GuestMealViewSet

router = DefaultRouter()
router.register(r"", GuestMealViewSet, basename="guestmeal")

urlpatterns = [
    path("", include(router.urls)),
]
