from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.months.models import Month


class Deposit(models.Model):
    CASH = "CASH"
    BKASH = "BKASH"
    NAGAD = "NAGAD"
    BANK = "BANK"
    PAYMENT_METHOD_CHOICES = [(CASH, "Cash"), (BKASH, "Bkash"), (NAGAD, "Nagad"), (BANK, "Bank")]

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    STATUS_CHOICES = [(PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected")]

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deposits")
    month = models.ForeignKey(Month, on_delete=models.PROTECT, related_name="deposits")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_reference = models.CharField(max_length=255, blank=True)
    payment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_deposits")
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [models.CheckConstraint(check=models.Q(amount__gt=0), name="check_deposit_amount_positive")]

    def __str__(self) -> str:
        return f"{self.member} - {self.amount}"
