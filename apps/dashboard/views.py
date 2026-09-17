import datetime
import json
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from apps.catalog.models import Category, Product
from apps.inventory.models import StockMovement
from apps.purchasing.models import Purchase
from apps.sales.models import Sale


class DashboardView(LoginRequiredMixin, TemplateView):
    """Real-time analytics and operations dashboard View."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        month_start = today.replace(day=1)

        # -------------------------------------------------------------------
        # 1. KPI COUNTER METRICS
        # -------------------------------------------------------------------
        # Valuation based on purchase cost
        valuation_metrics = Product.objects.alive().aggregate(
            total_val=Sum(F("current_stock") * F("purchase_price"))
        )
        context["stock_valuation"] = valuation_metrics["total_val"] or Decimal(
            "0.00"
        )

        # Low stock alert count
        context["low_stock_alerts_count"] = (
            Product.objects.alive()
            .filter(current_stock__lte=F("minimum_stock"))
            .count()
        )

        # Monthly Sales Revenue
        sales_metrics = Sale.objects.filter(
            status=Sale.Status.COMPLETED, sale_date__gte=month_start
        ).aggregate(total=Sum("grand_total"))
        context["monthly_sales_revenue"] = sales_metrics["total"] or Decimal(
            "0.00"
        )

        # Monthly Purchase Expenditure
        purchases_metrics = Purchase.objects.filter(
            status=Purchase.Status.RECEIVED, purchase_date__gte=month_start
        ).aggregate(total=Sum("grand_total"))
        context["monthly_purchases_expense"] = purchases_metrics[
            "total"
        ] or Decimal("0.00")

        # -------------------------------------------------------------------
        # 2. ACTIVITY & TABLES
        # -------------------------------------------------------------------
        # Recent stock movements (ledger timeline)
        context["recent_movements"] = (
            StockMovement.objects.select_related("product", "created_by")
            .order_by("-created_at")[:5]
        )

        # Recent sales invoices
        context["recent_sales"] = (
            Sale.objects.select_related("created_by")
            .order_by("-sale_date", "-created_at")[:5]
        )

        # Recent purchase orders
        context["recent_purchases"] = (
            Purchase.objects.select_related("supplier", "created_by")
            .order_by("-purchase_date", "-created_at")[:5]
        )

        # Low stock products list (max 5 alerts)
        context["low_stock_products"] = (
            Product.objects.alive()
            .filter(current_stock__lte=F("minimum_stock"))
            .order_by("current_stock")[:5]
        )

        # -------------------------------------------------------------------
        # 3. CHART DATA GRAPH GENERATION
        # -------------------------------------------------------------------
        # Line Chart: Sales vs Purchases Monthly Trend (last 6 months)
        months_labels = []
        sales_data = []
        purchases_data = []

        for i in range(5, -1, -1):
            # Safe month subtraction
            d = today - datetime.timedelta(days=i * 30)
            cur_month_start = d.replace(day=1)

            if cur_month_start.month == 12:
                next_month = cur_month_start.replace(
                    year=cur_month_start.year + 1, month=1
                )
            else:
                next_month = cur_month_start.replace(
                    month=cur_month_start.month + 1
                )
            cur_month_end = next_month - datetime.timedelta(days=1)

            months_labels.append(cur_month_start.strftime("%b %Y"))

            s_sum = (
                Sale.objects.filter(
                    status=Sale.Status.COMPLETED,
                    sale_date__range=[cur_month_start, cur_month_end],
                ).aggregate(total=Sum("grand_total"))["total"]
                or Decimal("0.00")
            )
            sales_data.append(float(s_sum))

            p_sum = (
                Purchase.objects.filter(
                    status=Purchase.Status.RECEIVED,
                    purchase_date__range=[cur_month_start, cur_month_end],
                ).aggregate(total=Sum("grand_total"))["total"]
                or Decimal("0.00")
            )
            purchases_data.append(float(p_sum))

        context["chart_months"] = json.dumps(months_labels)
        context["chart_sales"] = json.dumps(sales_data)
        context["chart_purchases"] = json.dumps(purchases_data)

        # Doughnut Chart: Category Valuations
        category_labels = []
        category_vals = []

        for cat in Category.objects.alive():
            val = (
                Product.objects.alive()
                .filter(category=cat)
                .aggregate(
                    total=Sum(F("current_stock") * F("purchase_price"))
                )["total"]
                or Decimal("0.00")
            )
            if val > 0:
                category_labels.append(cat.name)
                category_vals.append(float(val))

        context["chart_cat_labels"] = json.dumps(category_labels)
        context["chart_cat_vals"] = json.dumps(category_vals)

        return context
