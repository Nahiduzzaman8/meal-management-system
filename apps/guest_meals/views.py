from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.mixins import AuditLogMixin
from apps.guest_meals.models import GuestMeal
from apps.guest_meals.serializers import GuestMealDecisionSerializer, GuestMealSerializer
from apps.months.cache_utils import invalidate_month_estimate_cache
from apps.users.permissions import HasCapability, HasCapabilityOrIsManager


class GuestMealViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = GuestMeal.objects.all().order_by("meal_date")
    serializer_class = GuestMealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.has_capability("guest_meal.view_all"):
            return GuestMeal.objects.all().order_by("meal_date")
        return GuestMeal.objects.filter(member=user).order_by("meal_date")

    def get_permissions(self):
        if self.action == "create":
            self.required_capability = "guest_meal.submit"
            return [HasCapability()]
        if self.action in {"approve", "reject"}:
            self.required_capability = "guest_meal.approve"
            return [HasCapabilityOrIsManager()]
        if self.action in {"list", "retrieve"}:
            self.required_capability = "guest_meal.view_all" if self.request.user.has_capability("guest_meal.view_all") else "guest_meal.view_own"
            return [HasCapability()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save()
        invalidate_month_estimate_cache(instance.month_id)
        self._audit(
            action="GUEST_MEAL_CREATED",
            instance=instance,
            new_values={"id": instance.id, "member_id": instance.member_id, "meal_date": str(instance.meal_date), "lunch_quantity": instance.lunch_quantity, "dinner_quantity": instance.dinner_quantity},
            description=f"Guest meal created for {instance.member.username} on {instance.meal_date}",
        )
        return instance

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        guest_meal = self.get_object()
        if guest_meal.status == GuestMeal.REJECTED:
            return Response({"detail": "Rejected guest meals cannot be approved."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = GuestMealDecisionSerializer(guest_meal, data={"decision": "approved", "reason": request.data.get("reason", "")}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        guest_meal = serializer.save()
        invalidate_month_estimate_cache(guest_meal.month_id)
        self._audit(
            action="GUEST_MEAL_APPROVED",
            instance=guest_meal,
            old_values={"status": GuestMeal.PENDING},
            new_values={"status": guest_meal.status, "processed_by": guest_meal.processed_by_id},
            description=f"Guest meal approved for {guest_meal.member.username} on {guest_meal.meal_date}",
        )
        return Response(GuestMealSerializer(guest_meal).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        guest_meal = self.get_object()
        if guest_meal.status == GuestMeal.APPROVED:
            return Response({"detail": "Approved guest meals cannot be rejected."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = GuestMealDecisionSerializer(guest_meal, data={"decision": "rejected", "reason": request.data.get("reason", "")}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        guest_meal = serializer.save()
        invalidate_month_estimate_cache(guest_meal.month_id)
        self._audit(
            action="GUEST_MEAL_REJECTED",
            instance=guest_meal,
            old_values={"status": GuestMeal.PENDING},
            new_values={"status": guest_meal.status, "processed_by": guest_meal.processed_by_id, "rejection_reason": guest_meal.rejection_reason},
            description=f"Guest meal rejected for {guest_meal.member.username} on {guest_meal.meal_date}",
        )
        return Response(GuestMealSerializer(guest_meal).data, status=status.HTTP_200_OK)
