from __future__ import annotations

from django.db import models


class SystemSetting(models.Model):
    mess_name = models.CharField(max_length=255)
    mess_address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    meal_submission_deadline = models.TimeField()
    timezone = models.CharField(max_length=100, default="Asia/Dhaka")
    currency = models.CharField(max_length=20, default="BDT")
    guest_meal_enabled = models.BooleanField(default=True)
    notifications_enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["id"], name="single_system_setting")]

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.mess_name or "System Settings"
