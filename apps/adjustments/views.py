from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.adjustments.models import Adjustment
from apps.adjustments.serializers import AdjustmentSerializer
from apps.audit.mixins import AuditLogMixin
from apps.months.models import Month
from apps.users.permissions import HasCapability


class AdjustmentViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Adjustment.objects.all().order_by("-created_at")
    serializer_class = AdjustmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Adjustment.objects.all().order_by("-created_at")

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            self.required_capability = "adjustment.create"
            return [HasCapability()]
        if self.action in {"create", "update", "partial_update"}:
            self.required_capability = "adjustment.create"
            return [HasCapability()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        adjustment = serializer.save()
        return Response(self.get_serializer(adjustment).data, status=status.HTTP_201_CREATED)
