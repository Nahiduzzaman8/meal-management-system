from __future__ import annotations

from rest_framework import serializers

from apps.deposits.models import Deposit
from apps.months.models import Month


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = [
            "id",
            "member",
            "month",
            "amount",
            "payment_method",
            "transaction_reference",
            "payment_date",
            "status",
            "rejection_reason",
            "submitted_at",
            "processed_at",
            "processed_by",
            "note",
        ]
        read_only_fields = [
            "id",
            "member",
            "month",
            "status",
            "rejection_reason",
            "submitted_at",
            "processed_at",
            "processed_by",
        ]

    def validate(self, attrs):
        amount = attrs.get("amount")
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})

        payment_method = attrs.get("payment_method")
        transaction_reference = attrs.get("transaction_reference", "")
        if payment_method != Deposit.CASH and not transaction_reference.strip():
            raise serializers.ValidationError({"transaction_reference": "This field is required when payment_method is not CASH."})

        open_month = Month.objects.filter(status=Month.OPEN).first()
        if not open_month:
            raise serializers.ValidationError({"code": "month_not_open", "message": "Deposits are only allowed in the currently OPEN month."})

        month = attrs.get("month") or open_month
        if month.status != Month.OPEN:
            raise serializers.ValidationError({"code": "month_not_open", "message": "Deposits are only allowed in the currently OPEN month."})

        payment_date = attrs.get("payment_date")
        if payment_date is not None and not (open_month.start_date <= payment_date <= open_month.end_date):
            raise serializers.ValidationError({"payment_date": "Payment date must fall within the currently OPEN month."})

        attrs["month"] = open_month
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["member"] = request.user
        return super().create(validated_data)


class DepositDecisionSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Deposit
        fields = ["reason"]
