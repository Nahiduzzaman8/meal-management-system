from __future__ import annotations

import uuid

from django.forms import model_to_dict

from apps.audit.models import AuditLog


class AuditLogMixin:
    """Reusable audit hook for create/update/delete actions on DRF viewsets."""

    def _request_id(self):
        request = getattr(self, "request", None)
        if request is None:
            return None
        request_id = getattr(request, "request_id", None)
        if request_id is None:
            request_id = uuid.uuid4()
            request.request_id = request_id
        return request_id

    def _audit(self, *, action, instance, old_values=None, new_values=None, description=""):
        if instance is None:
            return
        request = getattr(self, "request", None)
        AuditLog.objects.create(
            actor=getattr(request, "user", None),
            action=action,
            entity_type=instance.__class__.__name__,
            entity_id=getattr(instance, "pk", None),
            old_values=old_values,
            new_values=new_values,
            description=description,
            request_id=self._request_id(),
            ip_address=(request.META.get("REMOTE_ADDR") if request else None),
        )

    def _serialize_instance(self, instance):
        if instance is None:
            return None
        fields = [field.name for field in instance._meta.fields]
        return model_to_dict(instance, fields=fields)

    def perform_create(self, serializer):
        instance = serializer.save()
        self._audit(
            action="CREATE",
            instance=instance,
            new_values=self._serialize_instance(instance),
            description=f"Created {instance.__class__.__name__} #{instance.pk}",
        )
        return instance

    def perform_update(self, serializer):
        instance = self.get_object()
        old_values = self._serialize_instance(instance)
        updated = serializer.save()
        self._audit(
            action="UPDATE",
            instance=updated,
            old_values=old_values,
            new_values=self._serialize_instance(updated),
            description=f"Updated {updated.__class__.__name__} #{updated.pk}",
        )
        return updated

    def perform_destroy(self, instance):
        old_values = self._serialize_instance(instance)
        instance.delete()
        self._audit(
            action="DELETE",
            instance=instance,
            old_values=old_values,
            new_values=None,
            description=f"Deleted {instance.__class__.__name__} #{instance.pk}",
        )
