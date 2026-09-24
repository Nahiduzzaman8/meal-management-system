from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.deposits.models import Deposit
from apps.guest_meals.models import GuestMeal
from apps.months.models import ManagerAssignment, Month, MonthMember
from apps.months.serializers import ManagerAssignmentSerializer, MonthMemberSerializer, MonthSerializer
from apps.months.services import close_month, warn_open_month_ending_soon
from apps.users.permissions import HasCapability
from apps.users.models import User


class MonthViewSet(viewsets.ModelViewSet):
    queryset = Month.objects.all().order_by("start_date")
    serializer_class = MonthSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        perms = super().get_permissions()
        if self.action in {"create", "list", "retrieve", "update", "partial_update", "destroy"}:
            self.required_capability = "month.create" if self.action == "create" else "month.view"
        elif self.action == "open":
            self.required_capability = "month.open"
        elif self.action == "close":
            self.required_capability = "month.close"
        elif self.action == "reopen":
            self.required_capability = "month.reopen"
        elif self.action == "members":
            self.required_capability = "month.view"
        elif self.action == "assign_manager":
            self.required_capability = "manager.assign"
        return [HasCapability() for _ in perms]

    def list(self, request, *args, **kwargs):
        warning = warn_open_month_ending_soon()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        if warning:
            data["warning"] = warning
        return Response(data)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="open")
    def open(self, request, pk=None):
        month = self.get_object()
        if month.status != Month.PLANNED:
            return Response({"detail": "Only PLANNED months can be opened."}, status=status.HTTP_400_BAD_REQUEST)

        if Month.objects.filter(status=Month.OPEN).exists():
            return Response({"detail": "Another month is already OPEN."}, status=status.HTTP_400_BAD_REQUEST)

        month.status = Month.OPEN
        month.save(update_fields=["status", "updated_at"])

        member_queryset = User.objects.filter(is_active=True, role=User.MEMBER)
        for user in member_queryset:
            MonthMember.objects.get_or_create(
                month=month,
                member=user,
                defaults={
                    "joined_on": date.today(),
                    "opening_balance": self._latest_closing_balance(user),
                },
            )

        return Response(MonthSerializer(month).data, status=status.HTTP_200_OK)

    @staticmethod
    def _latest_closing_balance(member):
        previous = (
            MonthMember.objects.filter(member=member, month__status=Month.CLOSED)
            .order_by("-month__closed_at", "-month__id")
            .first()
        )
        if previous is None:
            return 0
        return previous.closing_balance or 0

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        idempotency_key = request.headers.get("Idempotency-Key")
        if idempotency_key:
            prior = AuditLog.objects.filter(
                action="MONTH_CLOSED",
                entity_type="Month",
                entity_id=int(pk),
                description__icontains=idempotency_key,
            ).first()
            if prior:
                return Response({"detail": "Month closure already processed."}, status=status.HTTP_200_OK)

        with transaction.atomic():
            month = Month.objects.select_for_update().get(pk=pk)
            failures = []

            if month.status != Month.OPEN:
                failures.append("Month must be OPEN to close.")
            if Deposit.objects.filter(month=month, status=Deposit.PENDING).exists():
                failures.append("There are pending deposits for this month.")
            if GuestMeal.objects.filter(month=month, status=GuestMeal.PENDING).exists():
                failures.append("There are pending guest meals for this month.")
            if month.final_total_meal_units is not None:
                pass
            if not month.meals.exists():
                failures.append("Countable meal units must be greater than zero.")
            if not Expense.objects.filter(month=month, is_deleted=False).exists():
                failures.append("Total non-deleted expense amount must be greater than zero.")
            if not MonthMember.objects.filter(month=month, left_on__isnull=True).exists():
                failures.append("At least one active MonthMember is required.")
            if not ManagerAssignment.objects.filter(month=month, unassigned_at__isnull=True).exists():
                failures.append("A currently active ManagerAssignment is required.")

            if failures:
                return Response({"code": "month_close_blocked", "failures": failures}, status=status.HTTP_400_BAD_REQUEST)

            month.closed_by = request.user
            month.closed_at = timezone.now()
            month = close_month(month)
            AuditLog.objects.create(
                actor=request.user,
                action="MONTH_CLOSED",
                entity_type="Month",
                entity_id=month.id,
                new_values={"status": "CLOSED"},
                description=f"Month closed with Idempotency-Key: {idempotency_key}" if idempotency_key else "Month closed.",
            )
            return Response(MonthSerializer(month).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen(self, request, pk=None):
        month = self.get_object()
        if month.status != Month.CLOSED:
            return Response({"detail": "Only CLOSED months can be reopened."}, status=status.HTTP_400_BAD_REQUEST)

        if Month.objects.filter(status=Month.OPEN).exists():
            return Response({"detail": "Another month is already OPEN."}, status=status.HTTP_400_BAD_REQUEST)

        serialized = {
            "final_fields": MonthSerializer(month).data,
            "members": list(month.members.all().values()),
        }
        AuditLog.objects.create(
            actor=request.user,
            action="MONTH_REOPENED",
            entity_type="Month",
            entity_id=month.id,
            old_values=serialized,
            new_values={"status": "OPEN"},
            description=f"Month reopened: {month.name}",
        )

        month.final_meal_rate = None
        month.final_total_expense = None
        month.final_total_meal_units = None
        month.rounding_residual = None
        month.closed_at = None
        month.closed_by = None
        month.status = Month.OPEN
        month.reopened_count = (month.reopened_count or 0) + 1
        month.last_reopened_at = timezone.now()
        month.save(update_fields=[
            "final_meal_rate",
            "final_total_expense",
            "final_total_meal_units",
            "rounding_residual",
            "closed_at",
            "closed_by",
            "status",
            "reopened_count",
            "last_reopened_at",
            "updated_at",
        ])

        MonthMember.objects.filter(month=month).update(finalized_at=None)
        return Response(MonthSerializer(month).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, pk=None):
        month = self.get_object()
        queryset = month.members.all().order_by("member__id")
        serializer = MonthMemberSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["put"], url_path="manager")
    def assign_manager(self, request, pk=None):
        month = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not target.is_active:
            return Response({"detail": "Target user is inactive."}, status=status.HTTP_400_BAD_REQUEST)
        if target.role != User.MEMBER:
            return Response({"detail": "Target user must have MEMBER role."}, status=status.HTTP_400_BAD_REQUEST)

        current = ManagerAssignment.objects.filter(month=month, unassigned_at__isnull=True).first()
        if current and current.user_id == target.id:
            return Response({"detail": "Target user is already the current manager."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if current:
                current.unassigned_at = timezone.now()
                current.unassigned_by = request.user
                current.save(update_fields=["unassigned_at", "unassigned_by"])

            assignment = ManagerAssignment.objects.create(
                month=month,
                user=target,
                assigned_by=request.user,
            )

        return Response(ManagerAssignmentSerializer(assignment).data, status=status.HTTP_200_OK)


# Keep this import available for the month lifecycle API.
from apps.expenses.models import Expense
