from django.db.models import Q
from django.views.generic import ListView

from apps.accounts.decorators import RoleRequiredMixin
from apps.accounts.models import Role
from apps.audit.models import AuditLog


class AuditLogListView(RoleRequiredMixin, ListView):
    """Admin-only panel to review system-wide audit records chronologically."""

    model = AuditLog
    template_name = "audit/audit_list.html"
    context_object_name = "logs"
    paginate_by = 25
    allowed_roles = [Role.Name.ADMINISTRATOR]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related("user").order_by("-timestamp")

        # Search filter
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(user__email__icontains=search_query)
                | Q(action__icontains=search_query)
                | Q(model_name__icontains=search_query)
                | Q(object_repr__icontains=search_query)
                | Q(details__icontains=search_query)
            )

        # Action filter
        action_filter = self.request.GET.get("action", "").strip()
        if action_filter:
            queryset = queryset.filter(action=action_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["action_filter"] = self.request.GET.get("action", "").strip()

        # Get unique actions for filtering dropdown
        context["actions"] = (
            AuditLog.objects.order_by("action")
            .values_list("action", flat=True)
            .distinct()
        )
        return context
