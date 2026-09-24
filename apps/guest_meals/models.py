from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.months.models import Month


class GuestMeal(models.Model):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    STATUS_CHOICES = [(PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected")]

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guest_meals")
    month = models.ForeignKey(Month, on_delete=models.PROTECT, related_name="guest_meals")
    meal_date = models.DateField()
    lunch_quantity = models.PositiveIntegerField(default=0)
    dinner_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    rejection_reason = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_guest_meals")

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(lunch_quantity__gt=0) | models.Q(dinner_quantity__gt=0), name="check_guest_meal_has_quantity"),
            models.UniqueConstraint(fields=["member", "meal_date"], condition=~models.Q(status="REJECTED"), name="unique_active_guest_meal_per_date"),
        ]

    def __str__(self) -> str:
        return f"{self.member} - {self.meal_date}"
