from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from apps.catalog.models import Supplier
from apps.purchasing.forms import PurchaseForm, PurchaseItemFormSet
from apps.purchasing.models import Purchase
from apps.purchasing.services import PurchasingService


class PurchaseListView(PermissionRequiredMixin, ListView):
    """Lists Purchase Orders with status filters and supplier lookup."""

    model = Purchase
    template_name = "purchasing/purchase_list.html"
    context_object_name = "purchases"
    paginate_by = 10
    permission_required = "purchasing.view_purchase"

    def get_queryset(self):
        queryset = Purchase.objects.select_related("supplier", "created_by")
        q = self.request.GET.get("q")
        supplier_id = self.request.GET.get("supplier")
        status = self.request.GET.get("status")

        if q:
            queryset = queryset.filter(purchase_number__icontains=q)

        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-purchase_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["selected_supplier"] = self.request.GET.get("supplier", "")
        context["selected_status"] = self.request.GET.get("status", "")

        context["suppliers"] = Supplier.objects.alive().filter(is_active=True).order_by("company_name")
        context["statuses"] = Purchase.Status.choices
        return context


class PurchaseDetailView(PermissionRequiredMixin, DetailView):
    """Detailed view for a Purchase Order showing item ledger list and totals."""

    model = Purchase
    template_name = "purchasing/purchase_detail.html"
    context_object_name = "purchase"
    permission_required = "purchasing.view_purchase"

    def get_queryset(self):
        return Purchase.objects.select_related("supplier", "created_by").prefetch_related("items__product")


class PurchaseCreateView(PermissionRequiredMixin, CreateView):
    """Form view to create a Purchase Order with inline items formset."""

    model = Purchase
    form_class = PurchaseForm
    template_name = "purchasing/purchase_form.html"
    permission_required = "purchasing.add_purchase"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = PurchaseItemFormSet(self.request.POST)
        else:
            context["formset"] = PurchaseItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        user = self.request.user
        assert not user.is_anonymous

        if formset.is_valid():
            # Extract fields
            supplier = form.cleaned_data["supplier"]
            purchase_date = form.cleaned_data["purchase_date"]
            tax = form.cleaned_data["tax"]
            discount = form.cleaned_data["discount"]
            notes = form.cleaned_data["notes"]

            # Format items data
            items_data = []
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get("DELETE", False):
                    items_data.append({
                        "product": item_form.cleaned_data["product"],
                        "quantity": item_form.cleaned_data["quantity"],
                        "unit_price": item_form.cleaned_data["unit_price"],
                    })

            if not items_data:
                form.add_error(None, "You must add at least one product line item.")
                return self.form_invalid(form)

            try:
                purchase = PurchasingService.create_purchase(
                    supplier=supplier,
                    purchase_date=purchase_date,
                    items_data=items_data,
                    user=user,
                    discount=discount,
                    tax=tax,
                    notes=notes,
                )
                messages.success(
                    self.request,
                    f"Purchase Order {purchase.purchase_number} created successfully."
                )
                return redirect("purchasing:purchase_detail", pk=purchase.pk)
            except Exception as e:
                form.add_error(None, f"Transaction error: {str(e)}")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class PurchaseReceiveView(PermissionRequiredMixin, View):
    """Endpoint view to confirm receipt of goods for ordered purchases."""

    permission_required = "purchasing.change_purchase"

    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)
        user = request.user
        assert not user.is_anonymous

        try:
            PurchasingService.receive_purchase(purchase, user)
            messages.success(
                request,
                f"Successfully received inventory for Purchase Order {purchase.purchase_number}."
            )
        except Exception as e:
            messages.error(request, f"Error receiving purchase order: {str(e)}")

        return redirect("purchasing:purchase_detail", pk=purchase.pk)
