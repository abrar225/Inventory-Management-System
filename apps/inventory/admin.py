from django.contrib import admin

from apps.inventory.models import StockAdjustment, StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Admin configuration for the immutable Stock Movement Ledger."""

    list_display = [
        "created_at",
        "product",
        "movement_type",
        "reference_type",
        "quantity",
        "balance_after",
        "created_by",
    ]
    list_filter = ["movement_type", "reference_type", "created_at"]
    search_fields = ["product__name", "product__sku", "reason"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "created_at",
        "product",
        "movement_type",
        "reference_type",
        "reference_id",
        "quantity",
        "balance_after",
        "reason",
        "created_by",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    """Admin configuration for manual Stock Adjustments."""

    list_display = [
        "created_at",
        "product",
        "adjustment_type",
        "quantity",
        "created_by",
        "approved_by",
    ]
    list_filter = ["adjustment_type", "created_at"]
    search_fields = ["product__name", "product__sku", "reason"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "created_at",
        "product",
        "adjustment_type",
        "quantity",
        "reason",
        "created_by",
        "approved_by",
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
