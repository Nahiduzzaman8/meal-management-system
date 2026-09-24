from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q


class Month(models.Model):
    PLANNED = "PLANNED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    STATUS_CHOICES = [(PLANNED, "Planned"), (OPEN, "Open"), (CLOSED, "Closed")]

    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PLANNED)
    final_meal_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    final_total_expense = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    final_total_meal_units = models.PositiveIntegerField(null=True, blank=True)
    rounding_residual = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="closed_months")
    reopened_count = models.IntegerField(default=0)
    last_reopened_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_months")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(start_date__lt=models.F("end_date")), name="check_month_start_before_end"),
            models.UniqueConstraint(fields=["status"], condition=Q(status="OPEN"), name="unique_open_month"),
        ]

    def __str__(self) -> str:
        return self.name


class ManagerAssignment(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="manager_assignments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="managed_months")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assigned_manager_roles")
    unassigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="unassigned_manager_roles")
    assigned_at = models.DateTimeField(auto_now_add=True)
    unassigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["month"], condition=Q(unassigned_at__isnull=True), name="unique_active_manager_per_month"),
        ]

    @classmethod
    def current_manager(cls, month):
        assignment = cls.objects.filter(month=month, unassigned_at__isnull=True).select_related("user").first()
        return assignment.user if assignment else None

    def __str__(self) -> str:
        return f"{self.user} -> {self.month}"


class MonthMember(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="members")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="month_memberships")
    joined_on = models.DateField()
    left_on = models.DateField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lunch_count = models.PositiveIntegerField(default=0)
    dinner_count = models.PositiveIntegerField(default=0)
    meal_units = models.PositiveIntegerField(default=0)
    guest_lunch_count = models.PositiveIntegerField(default=0)
    guest_dinner_count = models.PositiveIntegerField(default=0)
    guest_meal_units = models.PositiveIntegerField(default=0)
    meal_rate_applied = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    meal_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    guest_meal_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    adjustment_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approved_deposit_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["month", "member"], name="unique_month_member")]

    def __str__(self) -> str:
        return f"{self.member} / {self.month}"
