from __future__ import annotations

from datetime import date

from django.db import transaction
from rest_framework import serializers

from apps.audit.models import AuditLog
from apps.months.models import ManagerAssignment, Month, MonthMember
from apps.users.models import User


class MonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "status",
            "final_meal_rate",
            "final_total_expense",
            "final_total_meal_units",
            "rounding_residual",
            "closed_at",
            "closed_by",
            "reopened_count",
            "last_reopened_at",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "final_meal_rate",
            "final_total_expense",
            "final_total_meal_units",
            "rounding_residual",
            "closed_at",
            "closed_by",
            "reopened_count",
            "last_reopened_at",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({"end_date": "end_date must be after start_date."})

        if start_date and end_date:
            overlap = Month.objects.filter(start_date__lt=end_date, end_date__gt=start_date).exists()
            if overlap:
                raise serializers.ValidationError({"non_field_errors": ["Month date range overlaps with an existing month."]})

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        return super().create(validated_data)


class MonthMemberSerializer(serializers.ModelSerializer):
    member_username = serializers.SerializerMethodField()

    class Meta:
        model = MonthMember
        fields = [
            "id",
            "member",
            "member_username",
            "month",
            "joined_on",
            "left_on",
            "opening_balance",
            "lunch_count",
            "dinner_count",
            "meal_units",
            "guest_lunch_count",
            "guest_dinner_count",
            "guest_meal_units",
            "meal_rate_applied",
            "meal_cost",
            "guest_meal_cost",
            "adjustment_total",
            "total_cost",
            "approved_deposit_total",
            "closing_balance",
            "finalized_at",
        ]
        read_only_fields = [
            "id",
            "member_username",
            "month",
            "joined_on",
            "opening_balance",
            "meal_rate_applied",
            "meal_cost",
            "guest_meal_cost",
            "adjustment_total",
            "total_cost",
            "approved_deposit_total",
            "closing_balance",
            "finalized_at",
        ]

    def get_member_username(self, obj):
        return obj.member.username


class ManagerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerAssignment
        fields = ["id", "month", "user", "assigned_by", "unassigned_by", "assigned_at", "unassigned_at"]
        read_only_fields = ["id", "month", "assigned_by", "assigned_at", "unassigned_at", "unassigned_by"]


class MonthReopenAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = ["id", "name", "status", "final_meal_rate", "final_total_expense", "final_total_meal_units", "rounding_residual", "closed_at"]

    def create_audit_for_reopen(self, month, request):
        members = list(month.members.all().values())
        data = {
            "final_fields": MonthReopenAuditSerializer(month).data,
            "members": members,
        }
        AuditLog.objects.create(
            actor=request.user,
            action="MONTH_REOPENED",
            entity_type="Month",
            entity_id=month.id,
            old_values={"final_fields": data["final_fields"], "members": data["members"]},
            new_values={"status": "OPEN"},
            description=f"Month reopened: {month.name}",
        )
