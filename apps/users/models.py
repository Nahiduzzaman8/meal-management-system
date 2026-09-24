from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.months.models import ManagerAssignment, Month


class User(AbstractUser):
    """Custom user model for mess membership and admin access."""

    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    ROLE_CHOICES = [(ADMIN, "Admin"), (MEMBER, "Member")]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    phone = models.CharField(max_length=20, blank=True)
    must_change_password = models.BooleanField(default=True)

    # username is intentionally immutable after creation. Serializer-layer validation
    # should enforce this and reject any attempts to change it.

    def has_capability(self, code: str) -> bool:
        if self.is_superuser:
            return True
        return RolePermission.objects.filter(role__name=self.role, permission__code=code).exists()

    def is_current_manager(self) -> bool:
        open_month = Month.objects.filter(status=Month.OPEN).first()
        if not open_month:
            return False
        return ManagerAssignment.current_manager(open_month) == self

    def current_capabilities(self):
        capabilities = set(RolePermission.objects.filter(role__name=self.role).values_list("permission__code", flat=True))
        if self.is_current_manager():
            capabilities.update(
                [
                    "month.view",
                    "meal.correct",
                    "meal.view_all",
                    "deposit.approve",
                    "guest_meal.approve",
                    "expense.create",
                    "expense.update",
                    "expense.delete",
                    "report.view_all",
                ]
            )
        return sorted(capabilities)

    def deactivate(self, *, actor=None):
        self.is_active = False
        self.save(update_fields=["is_active"])
        for token in OutstandingToken.objects.filter(user=self):
            BlacklistedToken.objects.get_or_create(token=token)
        return self


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.code


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="roles")

    class Meta:
        unique_together = (("role", "permission"),)
        constraints = [
            models.UniqueConstraint(fields=["role", "permission"], name="unique_role_permission"),
        ]

    def __str__(self) -> str:
        return f"{self.role.name}:{self.permission.code}"
