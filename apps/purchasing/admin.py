from django.contrib import admin

from apps.purchasing.models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = ["line_total"]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = [
        "purchase_number",
        "supplier",
        "purchase_date",
        "subtotal",
        "grand_total",
        "status",
    ]
    list_filter = ["status", "purchase_date", "supplier"]
    search_fields = ["purchase_number", "supplier__company_name"]
    inlines = [PurchaseItemInline]
    readonly_fields = ["purchase_number", "subtotal", "grand_total"]
