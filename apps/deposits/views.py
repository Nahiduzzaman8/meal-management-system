from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.mixins import AuditLogMixin
from apps.deposits.models import Deposit
from apps.deposits.serializers import DepositDecisionSerializer, DepositSerializer
from apps.months.models import Month
from apps.notifications.models import Notification
from apps.users.permissions import HasCapability, HasCapabilityOrIsManager


class DepositViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Deposit.objects.all().order_by("-submitted_at")
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Deposit.objects.all().order_by("-submitted_at")
        if user.is_superuser or user.has_capability("deposit.approve"):
            return qs
        return qs.filter(member=user)

    def get_permissions(self):
        if self.action in {"create", "list", "retrieve"}:
            self.required_capability = "deposit.approve" if self.request.user.has_capability("deposit.approve") else "deposit.view_own"
            return [HasCapability()]
        if self.action in {"approve", "reject"}:
            self.required_capability = "deposit.approve"
            return [HasCapabilityOrIsManager()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        open_month = Month.objects.filter(status=Month.OPEN).first()
        if not open_month:
            return Response({"code": "month_not_open", "message": "Deposits are only allowed against the currently OPEN month."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        deposit = serializer.save()
        return Response(self.get_serializer(deposit).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        deposit = self.get_object()
        if deposit.status != Deposit.PENDING:
            return Response({"detail": "Only PENDING deposits can be approved."}, status=status.HTTP_400_BAD_REQUEST)
        if deposit.month.status != Month.OPEN:
            return Response({"code": "month_closed", "message": "Deposits can only be approved while the month remains OPEN."}, status=status.HTTP_400_BAD_REQUEST)

        deposit.status = Deposit.APPROVED
        deposit.processed_by = request.user
        deposit.processed_at = __import__("django.utils.timezone").utils.timezone.now()
        deposit.save(update_fields=["status", "processed_by", "processed_at"])
        Notification.objects.create(
            user=deposit.member,
            type="deposit_approved",
            message=f"Your deposit of {deposit.amount} for {deposit.month.name} was approved.",
            entity_type="Deposit",
            entity_id=deposit.id,
        )
        return Response(self.get_serializer(deposit).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        deposit = self.get_object()
        reason = request.data.get("reason")
        if not reason or not str(reason).strip():
            return Response({"reason": "Reason is required."}, status=status.HTTP_400_BAD_REQUEST)
        if deposit.status != Deposit.PENDING:
            return Response({"detail": "Only PENDING deposits can be rejected."}, status=status.HTTP_400_BAD_REQUEST)
        if deposit.month.status != Month.OPEN:
            return Response({"code": "month_closed", "message": "Deposits can only be rejected while the month remains OPEN."}, status=status.HTTP_400_BAD_REQUEST)

        deposit.status = Deposit.REJECTED
        deposit.rejection_reason = reason
        deposit.processed_by = request.user
        deposit.processed_at = __import__("django.utils.timezone").utils.timezone.now()
        deposit.save(update_fields=["status", "rejection_reason", "processed_by", "processed_at"])
        Notification.objects.create(
            user=deposit.member,
            type="deposit_rejected",
            message=f"Your deposit of {deposit.amount} for {deposit.month.name} was rejected: {reason}",
            entity_type="Deposit",
            entity_id=deposit.id,
        )
        return Response(self.get_serializer(deposit).data, status=status.HTTP_200_OK)
