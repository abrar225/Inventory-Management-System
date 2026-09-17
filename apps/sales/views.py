from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, ListView

from apps.inventory.services import InsufficientStockError
from apps.sales.forms import SaleForm, SaleItemFormSet
from apps.sales.models import Sale
from apps.sales.services import SalesService


class SaleListView(PermissionRequiredMixin, ListView):
    """Lists Sale Invoices with search parameter checks."""

    model = Sale
    template_name = "sales/sale_list.html"
    context_object_name = "sales"
    paginate_by = 10
    permission_required = "sales.view_sale"

    def get_queryset(self):
        queryset = Sale.objects.select_related("created_by")
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(invoice_number__icontains=q)
        return queryset.order_by("-sale_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context


class SaleDetailView(PermissionRequiredMixin, DetailView):
    """Detailed view for a Sale Invoice representing print-ready receipts."""

    model = Sale
    template_name = "sales/sale_detail.html"
    context_object_name = "sale"
    permission_required = "sales.view_sale"

    def get_queryset(self):
        return Sale.objects.select_related("created_by").prefetch_related(
            "items__product"
        )


class SaleCreateView(PermissionRequiredMixin, CreateView):
    """Form view to record a Sale Invoice with stock availability checks."""

    model = Sale
    form_class = SaleForm
    template_name = "sales/sale_form.html"
    permission_required = "sales.add_sale"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = SaleItemFormSet(self.request.POST)
        else:
            context["formset"] = SaleItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        user = self.request.user
        assert not user.is_anonymous

        if formset.is_valid():
            customer_name = form.cleaned_data["customer_name"]
            sale_date = form.cleaned_data["sale_date"]
            tax = form.cleaned_data["tax"]
            discount = form.cleaned_data["discount"]

            items_data = []
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get(
                    "DELETE", False
                ):
                    items_data.append(
                        {
                            "product": item_form.cleaned_data["product"],
                            "quantity": item_form.cleaned_data["quantity"],
                            "unit_price": item_form.cleaned_data["unit_price"],
                        }
                    )

            if not items_data:
                form.add_error(None, "You must add at least one line item.")
                return self.form_invalid(form)

            try:
                sale = SalesService.create_sale(
                    customer_name=customer_name,
                    sale_date=sale_date,
                    items_data=items_data,
                    user=user,
                    discount=discount,
                    tax=tax,
                )
                messages.success(
                    self.request,
                    f"Invoice {sale.invoice_number} created successfully.",
                )
                return redirect("sales:sale_detail", pk=sale.pk)
            except InsufficientStockError as e:
                form.add_error(None, str(e))
                return self.form_invalid(form)
            except Exception as e:
                form.add_error(None, f"Transaction error: {str(e)}")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)
