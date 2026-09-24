from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from django.utils import timezone

from apps.adjustments.models import Adjustment
from apps.deposits.models import Deposit
from apps.expenses.models import Expense
from apps.guest_meals.models import GuestMeal
from apps.meals.models import Meal
from apps.months.models import Month, MonthMember
from apps.notifications.models import Notification
from apps.users.models import User


def _decimal(value):
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def finalize_month(month: Month) -> Month:
    """Finalize a month after all rows for the month have been recorded."""
    if month.status != Month.OPEN:
        raise ValueError("Only OPEN months can be finalized.")

    countable_meal_units = 0
    for meal in Meal.objects.filter(month=month):
        countable_meal_units += int(meal.lunch) + int(meal.dinner)

    for guest_meal in GuestMeal.objects.filter(month=month, status=GuestMeal.APPROVED):
        countable_meal_units += int(guest_meal.lunch_quantity) + int(guest_meal.dinner_quantity)

    total_expense = Decimal("0")
    for expense in Expense.objects.filter(month=month):
        total_expense += _decimal(expense.amount)

    if countable_meal_units == 0:
        final_meal_rate = Decimal("0.0000")
    else:
        final_meal_rate = (total_expense / Decimal(countable_meal_units)).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )

    members = list(MonthMember.objects.filter(month=month).select_related("member"))
    for member_row in members:
        lunch_count = 0
        dinner_count = 0
        for meal in Meal.objects.filter(month=month, member=member_row.member):
            lunch_count += int(meal.lunch)
            dinner_count += int(meal.dinner)
        meal_units = lunch_count + dinner_count

        guest_lunch_count = 0
        guest_dinner_count = 0
        for guest_meal in GuestMeal.objects.filter(month=month, member=member_row.member, status=GuestMeal.APPROVED):
            guest_lunch_count += int(guest_meal.lunch_quantity)
            guest_dinner_count += int(guest_meal.dinner_quantity)
        guest_meal_units = guest_lunch_count + guest_dinner_count

        member_row.lunch_count = lunch_count
        member_row.dinner_count = dinner_count
        member_row.meal_units = meal_units
        member_row.guest_lunch_count = guest_lunch_count
        member_row.guest_dinner_count = guest_dinner_count
        member_row.guest_meal_units = guest_meal_units
        member_row.meal_rate_applied = final_meal_rate

        meal_cost = (Decimal(meal_units) * final_meal_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        guest_meal_cost = (Decimal(guest_meal_units) * final_meal_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        member_row.meal_cost = meal_cost
        member_row.guest_meal_cost = guest_meal_cost
        member_row.total_cost = meal_cost + guest_meal_cost

        adjustment_total = Decimal("0")
        for adjustment in Adjustment.objects.filter(month=month, member=member_row.member):
            amount = _decimal(adjustment.amount)
            if adjustment.direction == Adjustment.DEBIT:
                adjustment_total += amount
            elif adjustment.direction == Adjustment.CREDIT:
                adjustment_total -= amount
        member_row.adjustment_total = adjustment_total

        approved_deposit_total = Decimal("0")
        for deposit in Deposit.objects.filter(month=month, member=member_row.member, status=Deposit.APPROVED):
            approved_deposit_total += _decimal(deposit.amount)
        member_row.approved_deposit_total = approved_deposit_total

        member_row.closing_balance = (
            _decimal(member_row.opening_balance)
            + member_row.total_cost
            + member_row.adjustment_total
            - approved_deposit_total
        )
        member_row.save(update_fields=[
            "lunch_count",
            "dinner_count",
            "meal_units",
            "guest_lunch_count",
            "guest_dinner_count",
            "guest_meal_units",
            "meal_rate_applied",
            "meal_cost",
            "guest_meal_cost",
            "adjustment_total",
            "total_cost",
            "approved_deposit_total",
            "closing_balance",
        ])

    total_member_cost = sum(
        (_decimal(member_row.total_cost) for member_row in members),
        Decimal("0"),
    )
    residual = total_expense - total_member_cost

    if residual != 0:
        winner = None
        winner_score = None
        for member_row in members:
            score = member_row.meal_units + member_row.guest_meal_units
            if winner is None or winner_score is None or score > winner_score or (score == winner_score and member_row.member_id < winner.member_id):
                winner = member_row
                winner_score = score

        direction = Adjustment.DEBIT if residual > 0 else Adjustment.CREDIT
        adjustment_amount = abs(residual)
        system_user = User.objects.filter(username="system").first()
        if system_user is None:
            system_user = User.objects.create_user(
                username="system",
                password="system-pass-123",
                role=User.MEMBER,
                is_active=True,
            )

        adjustment = Adjustment.objects.create(
            month=month,
            member=winner.member,
            direction=direction,
            amount=adjustment_amount,
            reason="Automatic rounding residual allocation at month close",
            created_by=system_user,
        )

        if direction == Adjustment.DEBIT:
            winner.adjustment_total += _decimal(adjustment.amount)
        else:
            winner.adjustment_total -= _decimal(adjustment.amount)
        winner.closing_balance = (
            _decimal(winner.opening_balance)
            + winner.total_cost
            + winner.adjustment_total
            - _decimal(winner.approved_deposit_total)
        )
        winner.save(update_fields=["adjustment_total", "closing_balance"])
        month.rounding_residual = residual
    else:
        month.rounding_residual = Decimal("0.00")

    for member_row in MonthMember.objects.filter(month=month):
        member_row.finalized_at = timezone.now()
        member_row.save(update_fields=["finalized_at"])

    month.final_meal_rate = final_meal_rate
    month.final_total_expense = total_expense
    month.final_total_meal_units = countable_meal_units
    month.save(update_fields=["final_meal_rate", "final_total_expense", "final_total_meal_units", "rounding_residual", "updated_at"])

    for member_row in MonthMember.objects.filter(month=month).select_related("member"):
        Notification.objects.create(
            user=member_row.member,
            type="MONTH_CLOSED",
            message=f"Month {month.name} closed. Your closing balance is {member_row.closing_balance}.",
            entity_type="MonthMember",
            entity_id=member_row.id,
        )

    return month
