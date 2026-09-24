from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.mixins import AuditLogMixin
from apps.expenses.models import Expense
from apps.expenses.serializers import ExpenseSerializer
from apps.months.cache_utils import invalidate_month_estimate_cache
from apps.months.models import Month
from apps.users.permissions import HasCapabilityOrIsManager


class ExpenseViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by("-expense_date")
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.all().order_by("-expense_date")

    def get_permissions(self):
        if self.action in {"create", "list", "retrieve", "update", "partial_update"}:
            self.required_capability = "expense.create"
            return [HasCapabilityOrIsManager()]
        if self.action == "destroy":
            self.required_capability = "expense.delete"
            return [HasCapabilityOrIsManager()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        open_month = Month.objects.filter(status=Month.OPEN).first()
        if not open_month:
            return Response({"code": "month_not_open", "message": "Expenses are only allowed against the currently OPEN month."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()
        invalidate_month_estimate_cache(expense.month_id)
        return Response(self.get_serializer(expense).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if instance.month.status != Month.OPEN:
            return Response({"code": "month_closed", "message": "Expenses can only be updated while the month remains OPEN."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={"request": request})
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()
        invalidate_month_estimate_cache(expense.month_id)
        return Response(self.get_serializer(expense).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        reason = request.data.get("reason")
        if not reason or not str(reason).strip():
            return Response({"reason": "Reason is required."}, status=status.HTTP_400_BAD_REQUEST)

        expense = self.get_object()
        if expense.month.status != Month.OPEN:
            return Response({"code": "month_closed", "message": "Expenses can only be soft-deleted while the month remains OPEN."}, status=status.HTTP_400_BAD_REQUEST)

        expense.is_deleted = True
        expense.deleted_at = __import__("django.utils.timezone").utils.timezone.now()
        expense.deleted_by = request.user
        expense.delete_reason = reason
        expense.save(update_fields=["is_deleted", "deleted_at", "deleted_by", "delete_reason", "updated_at"])
        invalidate_month_estimate_cache(expense.month_id)
        return Response({"detail": "Expense marked as deleted."}, status=status.HTTP_200_OK)
