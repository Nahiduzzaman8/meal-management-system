from __future__ import annotations

from rest_framework import serializers

from apps.adjustments.models import Adjustment
from apps.months.models import Month


class AdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adjustment
        fields = [
            "id",
            "month",
            "member",
            "direction",
            "amount",
            "reason",
            "source_entity_type",
            "source_entity_id",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate(self, attrs):
        amount = attrs.get("amount")
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})

        reason = attrs.get("reason")
        if reason is not None and not reason.strip():
            raise serializers.ValidationError({"reason": "Reason is required."})

        month = attrs.get("month")
        if month is None:
            raise serializers.ValidationError({"month": "Month is required."})
        if month.status != Month.OPEN:
            raise serializers.ValidationError({"code": "month_not_open", "message": "Adjustments are only allowed against an OPEN month."})

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        return super().create(validated_data)
