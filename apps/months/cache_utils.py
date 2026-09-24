from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.core.cache import cache

from apps.expenses.models import Expense
from apps.guest_meals.models import GuestMeal
from apps.meals.models import Meal
from apps.months.models import Month

MONTH_ESTIMATED_RATE_CACHE_KEY = "month_estimated_rate:{month_id}"
MONTH_ESTIMATED_RATE_TTL = 60


def get_month_estimate_cache_key(month: Month | int) -> str:
    month_id = month.id if isinstance(month, Month) else month
    return MONTH_ESTIMATED_RATE_CACHE_KEY.format(month_id=month_id)


def invalidate_month_estimate_cache(month: Month | int | None) -> None:
    if month is None:
        return
    cache.delete(get_month_estimate_cache_key(month))


def get_estimated_month_snapshot(month: Month) -> dict:
    cache_key = get_month_estimate_cache_key(month)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    countable_meal_units = 0
    for meal in Meal.objects.filter(month=month):
        countable_meal_units += int(meal.lunch) + int(meal.dinner)
    for guest_meal in GuestMeal.objects.filter(month=month, status=GuestMeal.APPROVED):
        countable_meal_units += int(guest_meal.lunch_quantity) + int(guest_meal.dinner_quantity)

    total_expense = Decimal("0")
    for expense in Expense.objects.filter(month=month, is_deleted=False):
        total_expense += Decimal(str(expense.amount))

    if countable_meal_units == 0:
        estimated_rate = Decimal("0.0000")
    else:
        estimated_rate = (total_expense / Decimal(countable_meal_units)).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )

    snapshot = {
        "month_id": month.id,
        "countable_meal_units_so_far": countable_meal_units,
        "total_expense_so_far": total_expense,
        "estimated_rate": estimated_rate,
    }
    cache.set(cache_key, snapshot, timeout=MONTH_ESTIMATED_RATE_TTL)
    return snapshot
