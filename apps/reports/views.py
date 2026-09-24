from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deposits.models import Deposit
from apps.expenses.models import Expense
from apps.guest_meals.models import GuestMeal
from apps.months.cache_utils import get_estimated_month_snapshot, invalidate_month_estimate_cache
from apps.months.models import ManagerAssignment, Month, MonthMember
from apps.months.serializers import MonthMemberSerializer
from apps.reports.serializers import BalanceHistorySerializer, MonthlyReportSerializer
from apps.users.models import User


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_month = Month.objects.filter(status=Month.OPEN).order_by("start_date").first()
        current_member = None
        if current_month is not None:
            current_member = MonthMember.objects.filter(month=current_month, member=request.user).first()

        base_payload = {
            "current_month": None,
            "meal_units": 0,
            "guest_meal_units": 0,
            "closing_balance": Decimal("0.00"),
            "calculation_status": "ESTIMATED",
        }

        if current_month is not None:
            base_payload["current_month"] = {
                "id": current_month.id,
                "name": current_month.name,
                "status": current_month.status,
            }

        if current_member is not None:
            base_payload["meal_units"] = current_member.meal_units
            base_payload["guest_meal_units"] = current_member.guest_meal_units
            if current_member.finalized_at is not None:
                base_payload["closing_balance"] = current_member.closing_balance
                base_payload["calculation_status"] = "FINAL"
            else:
                estimate = get_estimated_month_snapshot(current_month)
                estimated_rate = estimate["estimated_rate"]
                live_units = current_member.meal_units + current_member.guest_meal_units
                live_total = (Decimal(live_units) * estimated_rate).quantize(Decimal("0.01"))
                base_payload["closing_balance"] = (
                    Decimal(str(current_member.opening_balance))
                    + live_total
                    + Decimal(str(current_member.adjustment_total))
                    - Decimal(str(current_member.approved_deposit_total))
                )
                base_payload["calculation_status"] = "ESTIMATED"

        manager_view = request.user.role == User.ADMIN or request.user.has_capability("report.view_all") or request.user.is_current_manager()

        if manager_view and current_month is not None:
            pending_deposits = Deposit.objects.filter(month=current_month, status=Deposit.PENDING).count()
            pending_guest_meals = GuestMeal.objects.filter(month=current_month, status=GuestMeal.PENDING).count()
            total_expense = Expense.objects.filter(month=current_month, is_deleted=False).aggregate(total=Sum("amount"))["total"] or Decimal("0")
            estimate = get_estimated_month_snapshot(current_month)

            base_payload["pending_deposit_count"] = pending_deposits
            base_payload["pending_guest_meal_count"] = pending_guest_meals
            base_payload["total_expense_so_far"] = total_expense
            base_payload["estimated_meal_rate"] = estimate["estimated_rate"]

        if request.user.role == User.ADMIN and current_month is not None:
            manager = ManagerAssignment.objects.filter(month=current_month, unassigned_at__isnull=True).select_related("user").first()
            base_payload["total_active_members"] = MonthMember.objects.filter(month=current_month, left_on__isnull=True).count()
            base_payload["current_manager"] = manager.user_id if manager else None
            base_payload["reopened_count"] = current_month.reopened_count or 0

        return Response(base_payload)


class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.has_capability("report.view_own") or request.user.has_capability("report.view_all") or request.user.is_current_manager()):
            return Response({"detail": "You do not have access to reports."}, status=status.HTTP_403_FORBIDDEN)

        month_id = request.query_params.get("month_id")
        if not month_id:
            return Response({"detail": "month_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        month = get_object_or_404(Month, pk=month_id)
        estimate = get_estimated_month_snapshot(month)
        if month.status == Month.CLOSED:
            payload = {
                "month_id": month.id,
                "month_name": month.name,
                "status": month.status,
                "calculation_status": "FINAL",
                "total_expense": month.final_total_expense or Decimal("0.00"),
                "total_meal_units": month.final_total_meal_units or 0,
                "meal_rate": month.final_meal_rate or Decimal("0.0000"),
                "rounding_residual": month.rounding_residual or Decimal("0.00"),
            }
        else:
            payload = {
                "month_id": month.id,
                "month_name": month.name,
                "status": month.status,
                "calculation_status": "ESTIMATED",
                "total_expense": estimate["total_expense_so_far"],
                "total_meal_units": estimate["countable_meal_units_so_far"],
                "meal_rate": estimate["estimated_rate"],
                "rounding_residual": Decimal("0.00"),
            }

        serializer = MonthlyReportSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class MembersReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.has_capability("report.view_own") or request.user.has_capability("report.view_all") or request.user.is_current_manager()):
            return Response({"detail": "You do not have access to member reports."}, status=status.HTTP_403_FORBIDDEN)

        month_id = request.query_params.get("month_id")
        if not month_id:
            return Response({"detail": "month_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        month = get_object_or_404(Month, pk=month_id)
        if request.user.has_capability("report.view_all") or request.user.is_current_manager():
            members = MonthMember.objects.filter(month=month).order_by("member__id")
            calculation_status = "FINAL" if month.status == Month.CLOSED else "ESTIMATED"
        else:
            members = MonthMember.objects.filter(month=month, member=request.user).order_by("member__id")
            calculation_status = "FINAL" if month.status == Month.CLOSED else "ESTIMATED"

        payload = {
            "month_id": month.id,
            "month_name": month.name,
            "status": month.status,
            "calculation_status": calculation_status,
            "members": MonthMemberSerializer(members, many=True).data,
        }
        return Response(payload)


class BalanceHistoryReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        member_id = request.query_params.get("member_id")
        if not member_id:
            return Response({"detail": "member_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        target_member_id = int(member_id)
        is_self = target_member_id == request.user.id
        can_view_all = request.user.has_capability("report.view_all") or request.user.is_current_manager()
        if not is_self and not can_view_all:
            return Response({"detail": "You can only view your own balance history unless you have report.view_all."}, status=status.HTTP_403_FORBIDDEN)

        rows = (
            MonthMember.objects.filter(member_id=target_member_id, finalized_at__isnull=False)
            .select_related("month")
            .order_by("month__start_date")
        )
        payload = {
            "member_id": target_member_id,
            "calculation_status": "FINAL",
            "history": BalanceHistorySerializer(
                [
                    {
                        "month_id": row.month_id,
                        "month_name": row.month.name,
                        "closing_balance": row.closing_balance,
                        "finalized_at": row.finalized_at,
                    }
                    for row in rows
                ],
                many=True,
            ).data,
        }
        return Response(payload)
