from apps.accounts.models import User
from apps.audit.models import AuditLog


class AuditService:
    """Business service layer for writing system audit logs."""

    @staticmethod
    def log(
        user: User | None,
        action: str,
        model_name: str = "",
        object_id: str = "",
        object_repr: str = "",
        details: str = "",
        ip_address: str | None = None,
    ) -> AuditLog:
        """Creates and saves a system audit log record."""
        return AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            details=details,
            ip_address=ip_address,
        )
