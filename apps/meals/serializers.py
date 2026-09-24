from __future__ import annotations

from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from apps.audit.models import AuditLog
from apps.meals.models import Meal
from apps.months.utils import resolve_month_for_date
from apps.settings_app.models import SystemSetting


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = [
            "id",
            "member",
            "month",
            "meal_date",
            "lunch",
            "dinner",
            "last_corrected_by",
            "last_corrected_at",
            "correction_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "member",
            "month",
            "last_corrected_by",
            "last_corrected_at",
            "correction_reason",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        meal_date = attrs.get("meal_date")
        if meal_date is None:
            return attrs

        month = resolve_month_for_date(meal_date)
        setting = SystemSetting.objects.first()
        if setting:
            deadline = timezone.make_aware(
                datetime.combine(meal_date, setting.meal_submission_deadline),
                timezone.get_current_timezone(),
            )
            if timezone.now() > deadline:
                raise serializers.ValidationError({
                    "code": "deadline_passed",
                    "message": "Meal submission deadline has passed for this date.",
                })

        attrs["month"] = month
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        meal_date = validated_data["meal_date"]
        member = request.user
        existing = Meal.objects.filter(member=member, meal_date=meal_date).first()
        if existing:
            for field, value in validated_data.items():
                setattr(existing, field, value)
            existing.save()
            return existing

        validated_data["member"] = member
        return super().create(validated_data)


class MealCorrectSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(required=True, min_length=10)

    class Meta:
        model = Meal
        fields = ["lunch", "dinner", "reason"]

    def validate(self, attrs):
        if not attrs.get("lunch") and not attrs.get("dinner"):
            raise serializers.ValidationError({"detail": "At least one of lunch or dinner must be selected."})
        return attrs

    def save(self, **kwargs):
        meal = self.instance
        old_values = {"lunch": meal.lunch, "dinner": meal.dinner, "correction_reason": meal.correction_reason}
        meal.lunch = self.validated_data["lunch"]
        meal.dinner = self.validated_data["dinner"]
        meal.correction_reason = self.validated_data["reason"]
        meal.last_corrected_by = self.context["request"].user
        meal.last_corrected_at = timezone.now()
        meal.save()

        AuditLog.objects.create(
            actor=self.context["request"].user,
            action="MEAL_CORRECTED",
            entity_type="Meal",
            entity_id=meal.id,
            old_values=old_values,
            new_values={"lunch": meal.lunch, "dinner": meal.dinner, "correction_reason": meal.correction_reason},
            description=f"Meal corrected for {meal.member.username} on {meal.meal_date}",
        )
        return meal
