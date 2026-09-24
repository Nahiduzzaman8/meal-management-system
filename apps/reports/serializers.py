from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from apps.months.models import MonthMember


class MonthlyReportSerializer(serializers.Serializer):
    month_id = serializers.IntegerField()
    month_name = serializers.CharField()
    status = serializers.CharField()
    calculation_status = serializers.ChoiceField(choices=["ESTIMATED", "FINAL"])
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    total_meal_units = serializers.IntegerField()
    meal_rate = serializers.DecimalField(max_digits=12, decimal_places=4, coerce_to_string=False)
    rounding_residual = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False, required=False, allow_null=True)


class MemberMonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthMember
        fields = [
            "id",
            "member",
            "month",
            "joined_on",
            "left_on",
            "meal_units",
            "guest_meal_units",
            "opening_balance",
            "adjustment_total",
            "approved_deposit_total",
            "closing_balance",
            "finalized_at",
        ]


class BalanceHistorySerializer(serializers.Serializer):
    month_id = serializers.IntegerField()
    month_name = serializers.CharField()
    closing_balance = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    finalized_at = serializers.DateTimeField(allow_null=True)
