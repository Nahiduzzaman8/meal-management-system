from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.months.models import Month


class Adjustment(models.Model):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    DIRECTION_CHOICES = [(DEBIT, "Debit"), (CREDIT, "Credit")]

    month = models.ForeignKey(Month, on_delete=models.PROTECT, related_name="adjustments")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="adjustments")
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    source_entity_type = models.CharField(max_length=100, blank=True)
    source_entity_id = models.BigIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_adjustments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(check=models.Q(amount__gt=0), name="check_adjustment_amount_positive")]

    def __str__(self) -> str:
        return f"{self.member} - {self.direction} {self.amount}"
