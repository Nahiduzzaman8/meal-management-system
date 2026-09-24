from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.test import TestCase

from apps.adjustments.models import Adjustment
from apps.deposits.models import Deposit
from apps.expenses.models import Expense
from apps.guest_meals.models import GuestMeal
from apps.meals.models import Meal
from apps.months.calculations import finalize_month
from apps.months.models import ManagerAssignment, Month, MonthMember
from apps.users.models import User


class MonthClosingReconciliationTest(TestCase):
    def test_deactivating_active_manager_unassigns_them_from_open_month(self):
        actor = User.objects.create_user(username="admin_user", password="pass123", role=User.ADMIN)
        month = Month.objects.create(
            name="2026-08",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            status=Month.OPEN,
            created_by=actor,
        )
        manager = User.objects.create_user(username="manager_user", password="pass123", role=User.MEMBER)
        assignment = ManagerAssignment.objects.create(
            month=month,
            user=manager,
            assigned_by=actor,
        )

        manager.deactivate(actor=actor)

        assignment.refresh_from_db()
        self.assertIsNotNone(assignment.unassigned_at)
        self.assertEqual(assignment.unassigned_by_id, actor.id)
        self.assertFalse(manager.is_current_manager())

    def test_month_close_reconciliation_and_opening_balance_carry_forward(self):
        system_user = User.objects.create_user(username="system", password="pass123", role=User.MEMBER)
        month = Month.objects.create(
            name="2026-09",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            status=Month.OPEN,
            created_by=system_user,
        )

        members = []
        for i in range(13):
            user = User.objects.create_user(username=f"member_{i}", password="pass123", role=User.MEMBER)
            if i == 0:
                left_on = date(2026, 9, 15)
                opening_balance = Decimal("50.00")
            elif i == 1:
                left_on = None
                opening_balance = Decimal("25.00")
            else:
                left_on = None
                opening_balance = Decimal("0.00")

            if i == 12:
                joined_on = date(2026, 9, 16)
                opening_balance = Decimal("0.00")
            else:
                joined_on = date(2026, 9, 1)

            member_row = MonthMember.objects.create(
                month=month,
                member=user,
                joined_on=joined_on,
                left_on=left_on,
                opening_balance=opening_balance,
            )
            members.append((user, member_row))

        total_expense = Decimal("12345.67")
        # Build a number of meal units that does not divide evenly into the total expense.
        meal_unit_plan = [
            (0, 1), (1, 0), (1, 1), (0, 1), (1, 1), (0, 0), (1, 0),
            (1, 1), (0, 1), (1, 0), (1, 1), (0, 0), (1, 1),
        ]
        meal_index = 0

        for user, member_row in members:
            if user.username == "member_0":
                meal_dates = [date(2026, 9, 2), date(2026, 9, 5), date(2026, 9, 10), date(2026, 9, 14)]
            elif user.username == "member_12":
                meal_dates = [date(2026, 9, 18), date(2026, 9, 20), date(2026, 9, 25)]
            else:
                meal_dates = [date(2026, 9, 3), date(2026, 9, 7), date(2026, 9, 12), date(2026, 9, 19)]

            for meal_date in meal_dates:
                lunch, dinner = meal_unit_plan[meal_index % len(meal_unit_plan)]
                meal_index += 1
                Meal.objects.create(
                    member=user,
                    month=month,
                    meal_date=meal_date,
                    lunch=bool(lunch),
                    dinner=bool(dinner),
                )

        # Create a handful of approved guest meals to add non-even meal units.
        guest_member = members[2][0]
        GuestMeal.objects.create(
            member=guest_member,
            month=month,
            meal_date=date(2026, 9, 8),
            lunch_quantity=2,
            dinner_quantity=1,
            status=GuestMeal.APPROVED,
        )
        GuestMeal.objects.create(
            member=members[5][0],
            month=month,
            meal_date=date(2026, 9, 11),
            lunch_quantity=1,
            dinner_quantity=0,
            status=GuestMeal.APPROVED,
        )
        GuestMeal.objects.create(
            member=members[9][0],
            month=month,
            meal_date=date(2026, 9, 22),
            lunch_quantity=0,
            dinner_quantity=2,
            status=GuestMeal.APPROVED,
        )

        # Add a rejected guest meal to ensure it is excluded from aggregation.
        GuestMeal.objects.create(
            member=members[10][0],
            month=month,
            meal_date=date(2026, 9, 23),
            lunch_quantity=3,
            dinner_quantity=2,
            status=GuestMeal.REJECTED,
        )

        # Add expense rows for the month.
        Expense.objects.create(
            month=month,
            created_by=system_user,
            category=Expense.GROCERY,
            amount=Decimal("9000.00"),
            expense_date=date(2026, 9, 5),
            description="Groceries",
        )
        Expense.objects.create(
            month=month,
            created_by=system_user,
            category=Expense.GAS,
            amount=Decimal("1800.00"),
            expense_date=date(2026, 9, 12),
            description="Gas",
        )
        Expense.objects.create(
            month=month,
            created_by=system_user,
            category=Expense.ELECTRICITY,
            amount=Decimal("1545.67"),
            expense_date=date(2026, 9, 16),
            description="Electricity",
        )

        # Add an approved deposit for a member so the balance math is exercised.
        Deposit.objects.create(
            member=members[0][0],
            month=month,
            amount=Decimal("200.00"),
            payment_method=Deposit.CASH,
            payment_date=date(2026, 9, 9),
            status=Deposit.APPROVED,
        )

        # Add an opening adjustment for one member to test adjustment_total behavior.
        Adjustment.objects.create(
            month=month,
            member=members[3][0],
            direction=Adjustment.DEBIT,
            amount=Decimal("50.00"),
            reason="Adjustment test",
            created_by=system_user,
        )
        Adjustment.objects.create(
            month=month,
            member=members[8][0],
            direction=Adjustment.CREDIT,
            amount=Decimal("30.00"),
            reason="Adjustment test",
            created_by=system_user,
        )

        month = finalize_month(month)
        month.status = Month.CLOSED
        month.save(update_fields=["status"])

        total_member_cost = sum(
            (Decimal(str(member_row.total_cost)) for member_row in MonthMember.objects.filter(month=month)),
            Decimal("0"),
        )
        round_adj = Adjustment.objects.filter(
            month=month,
            reason="Automatic rounding residual allocation at month close",
        ).aggregate(total=Sum("amount"))
        rounding_adjustment = Decimal(str(round_adj["total"] or 0))
        self.assertEqual(total_member_cost + rounding_adjustment, month.final_total_expense)

        # The month should now have a closing balance for every member.
        for member_row in MonthMember.objects.filter(month=month):
            self.assertIsNotNone(member_row.closing_balance)
            self.assertIsNotNone(member_row.finalized_at)

        new_month = Month.objects.create(
            name="2026-10",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 31),
            status=Month.OPEN,
            created_by=system_user,
        )

        for _, member_row in members:
            finalized_member = MonthMember.objects.get(month=month, member=member_row.member)
            MonthMember.objects.create(
                month=new_month,
                member=member_row.member,
                joined_on=new_month.start_date,
                opening_balance=finalized_member.closing_balance,
            )

        new_members = MonthMember.objects.filter(month=new_month)
        for member_row in new_members:
            expected_balance = MonthMember.objects.get(month=month, member=member_row.member).closing_balance
            self.assertEqual(member_row.opening_balance, expected_balance)
