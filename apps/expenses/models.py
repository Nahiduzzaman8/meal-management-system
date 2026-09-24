from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.months.models import Month


class ExpenseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Expense(models.Model):
    GROCERY = "Grocery"
    GAS = "Gas"
    ELECTRICITY = "Electricity"
    WATER = "Water"
    INTERNET = "Internet"
    CLEANING = "Cleaning"
    MAINTENANCE = "Maintenance"
    OTHERS = "Others"

    CATEGORY_CHOICES = [
        (GROCERY, "Grocery"),
        (GAS, "Gas"),
        (ELECTRICITY, "Electricity"),
        (WATER, "Water"),
        (INTERNET, "Internet"),
        (CLEANING, "Cleaning"),
        (MAINTENANCE, "Maintenance"),
        (OTHERS, "Others"),
    ]

    month = models.ForeignKey(Month, on_delete=models.PROTECT, related_name="expenses")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_expenses")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    description = models.TextField()
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="deleted_expenses")
    delete_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExpenseManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.CheckConstraint(check=models.Q(amount__gt=0), name="check_expense_amount_positive")]

    def __str__(self) -> str:
        return f"{self.category} - {self.amount}"
