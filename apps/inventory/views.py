from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from apps.catalog.models import Product
from apps.inventory.forms import StockAdjustmentForm
from apps.inventory.models import StockMovement
from apps.inventory.services import InsufficientStockError, InventoryService


class InventoryDashboardView(PermissionRequiredMixin, ListView):
    """Inventory dashboard showing stock levels and KPI statistics."""

    model = Product
    template_name = "inventory/dashboard.html"
    context_object_name = "products"
    paginate_by = 10
    permission_required = "catalog.view_product"

    def get_queryset(self):
        queryset = Product.objects.alive().select_related("category", "supplier")
        q = self.request.GET.get("q")
        category_id = self.request.GET.get("category")
        stock_status = self.request.GET.get("stock_status")

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(sku__icontains=q) | Q(barcode__icontains=q)
            )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if stock_status == "low":
            queryset = queryset.filter(current_stock__lte=F("minimum_stock"), current_stock__gt=0)
        elif stock_status == "out":
            queryset = queryset.filter(current_stock__lte=0)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.catalog.models import Category

        # Filter preservation parameters
        context["q"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_stock_status"] = self.request.GET.get("stock_status", "")

        # Selectable filter lists
        context["categories"] = Category.objects.alive().filter(is_active=True).order_by("name")

        # KPI Metrics
        context["total_products"] = Product.objects.alive().count()
        context["low_stock_count"] = Product.objects.alive().filter(
            current_stock__lte=F("minimum_stock"), current_stock__gt=0
        ).count()
        context["out_of_stock_count"] = Product.objects.alive().filter(
            current_stock__lte=0
        ).count()

        total_val = Product.objects.alive().aggregate(
            total=Sum(F("current_stock") * F("purchase_price"))
        )["total"]
        context["total_value"] = total_val or 0.0

        return context


class StockMovementListView(PermissionRequiredMixin, ListView):
    """Immutable stock ledger history view."""

    model = StockMovement
    template_name = "inventory/movement_list.html"
    context_object_name = "movements"
    paginate_by = 20
    permission_required = "inventory.view_stockmovement"

    def get_queryset(self):
        queryset = StockMovement.objects.select_related("product", "created_by")
        q = self.request.GET.get("q")
        movement_type = self.request.GET.get("movement_type")

        if q:
            queryset = queryset.filter(
                Q(product__name__icontains=q) | Q(product__sku__icontains=q)
            )

        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        return queryset.order_by("-created_at", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["selected_movement_type"] = self.request.GET.get("movement_type", "")
        context["movement_types"] = StockMovement.MovementType.choices
        return context


class StockAdjustmentCreateView(PermissionRequiredMixin, CreateView):
    """View to record a manual stock adjustment."""

    form_class = StockAdjustmentForm
    template_name = "inventory/adjustment_form.html"
    success_url = reverse_lazy("inventory:dashboard")
    permission_required = "inventory.add_stockadjustment"

    def get_initial(self):
        initial = super().get_initial()
        product_id = self.request.GET.get("product")
        if product_id:
            initial["product"] = product_id
        return initial

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        quantity = form.cleaned_data["quantity"]
        adjustment_type = form.cleaned_data["adjustment_type"]
        reason = form.cleaned_data["reason"]

        user = self.request.user
        assert not user.is_anonymous

        try:
            InventoryService.adjust_stock(
                product=product,
                quantity=quantity,
                adjustment_type=adjustment_type,
                reason=reason,
                created_by=user,
            )
            messages.success(self.request, "Stock adjustment recorded successfully.")
            return redirect(self.success_url)
        except InsufficientStockError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
