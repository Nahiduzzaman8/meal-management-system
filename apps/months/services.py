from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.months.calculations import finalize_month
from apps.months.models import Month


def close_month(month: Month):
    """Close an OPEN month and finalize the monthly calculations in the same locked transaction."""
    with transaction.atomic():
        month = Month.objects.select_for_update().get(pk=month.pk)
        if month.status != Month.OPEN:
            return month

        month = finalize_month(month)
        month.status = Month.CLOSED
        month.closed_at = timezone.now()
        month.save(update_fields=["status", "final_meal_rate", "final_total_expense", "final_total_meal_units", "rounding_residual", "closed_at", "updated_at"])
    return month


def warn_open_month_ending_soon():
    """Returns a warning when the OPEN month is ending within 3 days and no PLANNED month exists."""
    open_month = Month.objects.filter(status=Month.OPEN).order_by("start_date").first()
    if not open_month:
        return None

    planned_exists = Month.objects.filter(status=Month.PLANNED).exists()
    if planned_exists:
        return None

    delta = (open_month.end_date - date.today()).days
    if delta <= 3 and delta >= 0:
        return {
            "month_id": open_month.id,
            "month_name": open_month.name,
            "warning": "The current OPEN month ends in 3 days or less and no PLANNED month exists yet.",
            "days_remaining": delta,
        }

    return None
