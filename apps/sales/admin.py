from django.contrib import admin

from apps.sales.models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ["line_total"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "customer_name",
        "sale_date",
        "subtotal",
        "grand_total",
        "status",
    ]
    list_filter = ["status", "sale_date"]
    search_fields = ["invoice_number", "customer_name"]
    inlines = [SaleItemInline]
    readonly_fields = ["invoice_number", "subtotal", "grand_total"]
