from __future__ import annotations

from django.db import migrations


def seed_capabilities(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    Permission = apps.get_model("users", "Permission")
    RolePermission = apps.get_model("users", "RolePermission")

    capabilities = [
        "month.view",
        "month.create",
        "month.open",
        "month.close",
        "month.reopen",
        "manager.assign",
        "user.view",
        "user.create",
        "user.deactivate",
        "user.reset_password",
        "settings.manage",
        "adjustment.create",
        "audit.view",
        "meal.correct",
        "meal.view_all",
        "deposit.approve",
        "guest_meal.approve",
        "expense.create",
        "expense.update",
        "expense.delete",
        "report.view_all",
        "meal.submit",
        "meal.view_own",
        "deposit.submit",
        "deposit.view_own",
        "guest_meal.submit",
        "guest_meal.view_own",
        "report.view_own",
    ]

    permission_map = {}
    for code in capabilities:
        permission, _ = Permission.objects.get_or_create(
            code=code,
            defaults={"description": f"Capability for {code}"},
        )
        permission_map[code] = permission

    admin_role, _ = Role.objects.get_or_create(name="ADMIN")
    member_role, _ = Role.objects.get_or_create(name="MEMBER")

    for code in capabilities:
        RolePermission.objects.get_or_create(role=admin_role, permission=permission_map[code])

    member_capabilities = [
        "meal.submit",
        "meal.view_own",
        "deposit.submit",
        "deposit.view_own",
        "guest_meal.submit",
        "guest_meal.view_own",
        "report.view_own",
    ]
    for code in member_capabilities:
        RolePermission.objects.get_or_create(role=member_role, permission=permission_map[code])

    # IMPORTANT: there is no MANAGER role row. The system derives manager status from
    # the currently open month's ManagerAssignment row (unassigned_at IS NULL). Manager
    # capabilities are therefore granted at request time by checking the open month and
    # the current manager assignment, not by a stored role or RolePermission entry.


def reverse_seed_capabilities(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    Permission = apps.get_model("users", "Permission")
    RolePermission = apps.get_model("users", "RolePermission")

    RolePermission.objects.filter(role__name__in=["ADMIN", "MEMBER"]).delete()
    Role.objects.filter(name__in=["ADMIN", "MEMBER"]).delete()
    Permission.objects.filter(
        code__in=[
            "month.view",
            "month.create",
            "month.open",
            "month.close",
            "month.reopen",
            "manager.assign",
            "user.view",
            "user.create",
            "user.deactivate",
            "user.reset_password",
            "settings.manage",
            "adjustment.create",
            "audit.view",
            "meal.correct",
            "meal.view_all",
            "deposit.approve",
            "guest_meal.approve",
            "expense.create",
            "expense.update",
            "expense.delete",
            "report.view_all",
            "meal.submit",
            "meal.view_own",
            "deposit.submit",
            "deposit.view_own",
            "guest_meal.submit",
            "guest_meal.view_own",
            "report.view_own",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_capabilities, reverse_seed_capabilities),
    ]
