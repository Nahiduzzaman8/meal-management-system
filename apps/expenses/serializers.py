from __future__ import annotations

from rest_framework import serializers

from apps.expenses.models import Expense
from apps.months.models import Month


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "month",
            "created_by",
            "category",
            "amount",
            "expense_date",
            "description",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "delete_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "delete_reason",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        amount = attrs.get("amount")
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})

        description = attrs.get("description")
        if description is not None and not description.strip():
            raise serializers.ValidationError({"description": "Description is required."})

        month = attrs.get("month")
        if month is None:
            month = Month.objects.filter(status=Month.OPEN).first()
            if month is None:
                raise serializers.ValidationError({"code": "month_not_open", "message": "Expenses are only allowed against the currently OPEN month."})
            attrs["month"] = month

        if month.status != Month.OPEN:
            raise serializers.ValidationError({"code": "month_not_open", "message": "Expenses are only allowed against the currently OPEN month."})

        expense_date = attrs.get("expense_date")
        if expense_date is not None and not (month.start_date <= expense_date <= month.end_date):
            raise serializers.ValidationError({"expense_date": "Expense date must fall within the selected OPEN month."})

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        return super().create(validated_data)
