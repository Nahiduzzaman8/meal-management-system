from __future__ import annotations

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.mixins import AuditLogMixin
from apps.meals.models import Meal
from apps.meals.serializers import MealCorrectSerializer, MealSerializer
from apps.months.cache_utils import invalidate_month_estimate_cache
from apps.months.models import Month
from apps.users.permissions import HasCapability, HasCapabilityOrIsManager


class MealViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Meal.objects.all().order_by("meal_date")
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        month_id = self.request.query_params.get("month") or self.request.query_params.get("month_id")
        if user.is_superuser or user.has_capability("meal.view_all"):
            qs = Meal.objects.all()
        else:
            qs = Meal.objects.filter(member=user)

        if month_id:
            qs = qs.filter(month_id=month_id)
        return qs.order_by("meal_date")

    def get_permissions(self):
        if self.action == "create":
            self.required_capability = "meal.submit"
            return [HasCapability()]
        if self.action == "correct":
            self.required_capability = "meal.correct"
            return [HasCapabilityOrIsManager()]
        if self.action in {"list", "retrieve"}:
            self.required_capability = "meal.view_all" if self.request.user.has_capability("meal.view_all") else "meal.view_own"
            return [HasCapability()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        meal = serializer.save()
        invalidate_month_estimate_cache(meal.month_id)
        self._audit(
            action="MEAL_CREATED",
            instance=meal,
            new_values={"id": meal.id, "member_id": meal.member_id, "meal_date": str(meal.meal_date), "lunch": meal.lunch, "dinner": meal.dinner},
            description=f"Meal created for {meal.member.username} on {meal.meal_date}",
        )
        return Response(self.get_serializer(meal).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="correct")
    def correct(self, request, pk=None):
        meal = self.get_object()
        if meal.month.status == Month.CLOSED:
            return Response({"code": "month_closed", "message": "Cannot correct meals in a closed month."}, status=status.HTTP_400_BAD_REQUEST)

        old_values = {"lunch": meal.lunch, "dinner": meal.dinner, "correction_reason": meal.correction_reason}
        serializer = MealCorrectSerializer(meal, data=request.data, context={"request": request}, partial=True)
        serializer.is_valid(raise_exception=True)
        meal = serializer.save()
        invalidate_month_estimate_cache(meal.month_id)
        self._audit(
            action="MEAL_CORRECTED",
            instance=meal,
            old_values=old_values,
            new_values={"lunch": meal.lunch, "dinner": meal.dinner, "correction_reason": meal.correction_reason},
            description=f"Meal corrected for {meal.member.username} on {meal.meal_date}",
        )
        return Response(MealSerializer(meal).data, status=status.HTTP_200_OK)
