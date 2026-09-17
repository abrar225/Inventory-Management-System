import csv
import datetime
from decimal import Decimal

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from apps.catalog.models import Category, Product
from apps.purchasing.models import PurchaseItem
from apps.sales.models import SaleItem


def _parse_date(date_str: str, default: datetime.date) -> datetime.date:
    """Helper to safely parse standard ISO-8601 date strings."""
    if not date_str:
        return default
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return default


class ReportsDashboardView(PermissionRequiredMixin, TemplateView):
    """Reporting center dashboard view containing interactive tab data tables."""

    template_name = "reporting/reports_dashboard.html"
    permission_required = "catalog.view_product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # Categories for filter inputs
        context["categories"] = (
            Category.objects.alive().filter(is_active=True).order_by("name")
        )

        # -------------------------------------------------------------------
        # 1. INVENTORY VALUATION TAB
        # -------------------------------------------------------------------
        inv_products = Product.objects.alive()
        inv_cat = request.GET.get("inv_category")
        inv_status = request.GET.get("inv_status")

        if inv_cat:
            inv_products = inv_products.filter(category_id=inv_cat)

        if inv_status == "low":
            inv_products = inv_products.filter(current_stock__lte=F("minimum_stock"))
        elif inv_status == "out":
            inv_products = inv_products.filter(current_stock__lte=0)
        elif inv_status == "in":
            inv_products = inv_products.filter(current_stock__gt=F("minimum_stock"))

        context["inv_products"] = inv_products.order_by("name")
        context["selected_inv_cat"] = inv_cat or ""
        context["selected_inv_status"] = inv_status or ""

        # Computes metrics
        metrics = inv_products.aggregate(
            total_items=Sum("current_stock"),
            total_cost=Sum(F("current_stock") * F("purchase_price")),
            total_retail=Sum(F("current_stock") * F("selling_price")),
        )
        context["inv_total_qty"] = metrics["total_items"] or 0
        context["inv_cost_valuation"] = metrics["total_cost"] or Decimal("0.00")
        context["inv_retail_valuation"] = metrics["total_retail"] or Decimal("0.00")
        context["inv_potential_profit"] = (
            context["inv_retail_valuation"] - context["inv_cost_valuation"]
        )

        # -------------------------------------------------------------------
        # 2. SALES ANALYSIS TAB
        # -------------------------------------------------------------------
        today = timezone.localdate()
        thirty_days_ago = today - datetime.timedelta(days=30)

        sale_start = _parse_date(request.GET.get("sale_start", ""), thirty_days_ago)
        sale_end = _parse_date(request.GET.get("sale_end", ""), today)
        context["sale_start"] = sale_start.strftime("%Y-%m-%d")
        context["sale_end"] = sale_end.strftime("%Y-%m-%d")

        sale_items = SaleItem.objects.filter(
            sale__status="Completed", sale__sale_date__range=[sale_start, sale_end]
        ).select_related("sale", "product")

        context["sale_items"] = sale_items.order_by("-sale__sale_date", "-sale__created_at")

        sales_metrics = sale_items.aggregate(
            total_qty=Sum("quantity"),
            total_rev=Sum("line_total"),
        )
        context["sales_qty"] = sales_metrics["total_qty"] or 0
        context["sales_revenue"] = sales_metrics["total_rev"] or Decimal("0.00")
        context["sales_invoices_count"] = (
            sale_items.values("sale").distinct().count()
        )

        # -------------------------------------------------------------------
        # 3. PURCHASES ANALYSIS TAB
        # -------------------------------------------------------------------
        pur_start = _parse_date(request.GET.get("pur_start", ""), thirty_days_ago)
        pur_end = _parse_date(request.GET.get("pur_end", ""), today)
        context["pur_start"] = pur_start.strftime("%Y-%m-%d")
        context["pur_end"] = pur_end.strftime("%Y-%m-%d")

        purchase_items = PurchaseItem.objects.filter(
            purchase__status="Received",
            purchase__purchase_date__range=[pur_start, pur_end],
        ).select_related("purchase", "product")

        context["purchase_items"] = purchase_items.order_by(
            "-purchase__purchase_date", "-purchase__created_at"
        )

        purchases_metrics = purchase_items.aggregate(
            total_qty=Sum("quantity"),
            total_cost=Sum("line_total"),
        )
        context["purchases_qty"] = purchases_metrics["total_qty"] or 0
        context["purchases_cost"] = purchases_metrics["total_cost"] or Decimal(
            "0.00"
        )
        context["purchases_orders_count"] = (
            purchase_items.values("purchase").distinct().count()
        )

        return context


class InventoryValuationCSVExportView(PermissionRequiredMixin, View):
    """Streams the Inventory Valuation metrics table into standard CSV format."""

    permission_required = "catalog.view_product"

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="inventory_valuation_{timezone.localdate()}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "SKU",
                "Product Name",
                "Category",
                "Current Stock",
                "Unit",
                "Purchase Price (₹)",
                "Selling Price (₹)",
                "Cost Valuation (₹)",
                "Retail Valuation (₹)",
                "Potential Profit (₹)",
            ]
        )

        inv_products = Product.objects.alive().select_related("category")
        inv_cat = request.GET.get("inv_category")
        inv_status = request.GET.get("inv_status")

        if inv_cat:
            inv_products = inv_products.filter(category_id=inv_cat)

        if inv_status == "low":
            inv_products = inv_products.filter(current_stock__lte=F("minimum_stock"))
        elif inv_status == "out":
            inv_products = inv_products.filter(current_stock__lte=0)
        elif inv_status == "in":
            inv_products = inv_products.filter(current_stock__gt=F("minimum_stock"))

        for p in inv_products.order_by("name"):
            cost_val = p.current_stock * p.purchase_price
            retail_val = p.current_stock * p.selling_price
            profit = retail_val - cost_val
            writer.writerow(
                [
                    p.sku,
                    p.name,
                    p.category.name,
                    p.current_stock,
                    p.unit,
                    f"{p.purchase_price:.2f}",
                    f"{p.selling_price:.2f}",
                    f"{cost_val:.2f}",
                    f"{retail_val:.2f}",
                    f"{profit:.2f}",
                ]
            )

        return response


class SalesReportCSVExportView(PermissionRequiredMixin, View):
    """Streams the Sales transactions ledger analysis table into standard CSV."""

    permission_required = "catalog.view_product"

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="sales_report_{timezone.localdate()}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Invoice Number",
                "Customer Name",
                "Sale Date",
                "Product SKU",
                "Product Name",
                "Quantity Sold",
                "Unit Price (₹)",
                "Line Total (₹)",
            ]
        )

        today = timezone.localdate()
        thirty_days_ago = today - datetime.timedelta(days=30)
        sale_start = _parse_date(request.GET.get("sale_start", ""), thirty_days_ago)
        sale_end = _parse_date(request.GET.get("sale_end", ""), today)

        sale_items = SaleItem.objects.filter(
            sale__status="Completed", sale__sale_date__range=[sale_start, sale_end]
        ).select_related("sale", "product")

        for item in sale_items.order_by("-sale__sale_date", "-sale__created_at"):
            writer.writerow(
                [
                    item.sale.invoice_number,
                    item.sale.customer_name,
                    item.sale.sale_date.strftime("%Y-%m-%d"),
                    item.product.sku,
                    item.product.name,
                    item.quantity,
                    f"{item.unit_price:.2f}",
                    f"{item.line_total:.2f}",
                ]
            )

        return response


class PurchaseReportCSVExportView(PermissionRequiredMixin, View):
    """Streams Purchase Order supply receipts analysis table into standard CSV."""

    permission_required = "catalog.view_product"

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="purchases_report_{timezone.localdate()}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Purchase Number",
                "Supplier Name",
                "Purchase Date",
                "Product SKU",
                "Product Name",
                "Quantity Ordered",
                "Unit Price (₹)",
                "Line Total (₹)",
            ]
        )

        today = timezone.localdate()
        thirty_days_ago = today - datetime.timedelta(days=30)
        pur_start = _parse_date(request.GET.get("pur_start", ""), thirty_days_ago)
        pur_end = _parse_date(request.GET.get("pur_end", ""), today)

        purchase_items = PurchaseItem.objects.filter(
            purchase__status="Received",
            purchase__purchase_date__range=[pur_start, pur_end],
        ).select_related("purchase", "product", "purchase__supplier")

        for item in purchase_items.order_by(
            "-purchase__purchase_date", "-purchase__created_at"
        ):
            writer.writerow(
                [
                    item.purchase.purchase_number,
                    item.purchase.supplier.company_name,
                    item.purchase.purchase_date.strftime("%Y-%m-%d"),
                    item.product.sku,
                    item.product.name,
                    item.quantity,
                    f"{item.unit_price:.2f}",
                    f"{item.line_total:.2f}",
                ]
            )

        return response
