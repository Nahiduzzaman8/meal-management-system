from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.months.models import Month


def resolve_month_for_date(meal_date):
    """Return the active month covering the date, or raise a ValidationError."""
    month = (
        Month.objects.filter(
            start_date__lte=meal_date,
            end_date__gte=meal_date,
            status__in=[Month.PLANNED, Month.OPEN],
        )
        .order_by("start_date")
        .first()
    )
    if month is None:
        raise ValidationError({"code": "no_month_for_date", "message": "No PLANNED or OPEN month covers this meal date."})
    return month
