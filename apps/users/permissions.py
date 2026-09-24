from __future__ import annotations

from apps.months.models import ManagerAssignment, Month
from rest_framework.permissions import BasePermission


class HasCapability(BasePermission):
    """Require a capability code from the view's required_capability attribute."""

    message = "You do not have the required capability."

    def has_permission(self, request, view):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return False

        required_capability = getattr(view, "required_capability", None)
        if not required_capability:
            return False

        return request.user.has_capability(required_capability)


class HasCapabilityOrIsManager(BasePermission):
    """Allow manager-only capabilities derived from the open month assignment."""

    message = "You do not have the required capability or manager access."
    MANAGER_GRANTABLE_CAPABILITIES = {
        "month.view",
        "meal.correct",
        "meal.view_all",
        "deposit.approve",
        "guest_meal.approve",
        "expense.create",
        "expense.update",
        "expense.delete",
        "report.view_all",
    }

    def has_permission(self, request, view):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return False

        required_capability = getattr(view, "required_capability", None)
        if not required_capability:
            return False

        if request.user.has_capability(required_capability):
            return True

        if required_capability not in self.MANAGER_GRANTABLE_CAPABILITIES:
            return False

        open_month = Month.objects.filter(status=Month.OPEN).first()
        return bool(open_month and ManagerAssignment.current_manager(open_month) == request.user)
