from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.months.models import Month


class Meal(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meals")
    month = models.ForeignKey(Month, on_delete=models.PROTECT, related_name="meals")
    meal_date = models.DateField()
    lunch = models.BooleanField(default=False)
    dinner = models.BooleanField(default=False)
    last_corrected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="corrected_meals")
    last_corrected_at = models.DateTimeField(null=True, blank=True)
    correction_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["member", "meal_date"], name="unique_member_meal_date")]

    def resolve_month(self):
        month = Month.objects.filter(
            start_date__lte=self.meal_date,
            end_date__gte=self.meal_date,
            status__in=[Month.PLANNED, Month.OPEN],
        ).order_by("start_date").first()
        if not month:
            raise ValidationError("Meal date does not fall inside any PLANNED or OPEN month.")
        return month

    def save(self, *args, **kwargs):
        # Meal month is resolved server-side from meal_date. Outside code should not
        # supply or trust a client-provided month_id; this keeps the `month` FK consistent.
        if not self.month_id:
            self.month = self.resolve_month()
        else:
            resolved = self.resolve_month()
            if self.month_id != resolved.pk:
                raise ValidationError("meal.month must match the resolved month for meal_date.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.member} - {self.meal_date}"
