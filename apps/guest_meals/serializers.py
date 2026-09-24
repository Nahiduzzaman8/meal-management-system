from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from apps.guest_meals.models import GuestMeal
from apps.months.utils import resolve_month_for_date


class GuestMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestMeal
        fields = [
            "id",
            "member",
            "month",
            "meal_date",
            "lunch_quantity",
            "dinner_quantity",
            "status",
            "rejection_reason",
            "remarks",
            "submitted_at",
            "processed_at",
            "processed_by",
        ]
        read_only_fields = [
            "id",
            "member",
            "month",
            "status",
            "submitted_at",
            "processed_at",
            "processed_by",
        ]

    def validate(self, attrs):
        meal_date = attrs.get("meal_date")
        if meal_date is None:
            return attrs

        month = resolve_month_for_date(meal_date)
        attrs["month"] = month

        qs = GuestMeal.objects.filter(member=self.context["request"].user, meal_date=meal_date)
        if self.instance is None and qs.exists():
            raise serializers.ValidationError({"meal_date": "You already submitted a guest meal for this date."})

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["member"] = request.user
        validated_data["status"] = GuestMeal.PENDING
        return super().create(validated_data)


class GuestMealDecisionSerializer(serializers.ModelSerializer):
    decision = serializers.ChoiceField(choices=[("approved", "approved"), ("rejected", "rejected")])
    reason = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = GuestMeal
        fields = ["decision", "reason"]

    def validate(self, attrs):
        decision = attrs["decision"]
        if decision == "approved" and self.instance is None:
            raise serializers.ValidationError({"decision": "A guest meal must exist before approval."})
        return attrs

    def save(self, **kwargs):
        meal = self.instance
        decision = self.validated_data["decision"]
        reason = self.validated_data.get("reason", "")
        user = self.context["request"].user

        if decision == "approved":
            meal.status = GuestMeal.APPROVED
            meal.rejection_reason = ""
            meal.remarks = reason or meal.remarks
        else:
            meal.status = GuestMeal.REJECTED
            meal.rejection_reason = reason or meal.rejection_reason
            meal.remarks = meal.remarks

        meal.processed_by = user
        meal.processed_at = timezone.now()
        meal.save()
        return meal
