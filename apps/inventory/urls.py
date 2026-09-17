from django.urls import path

from apps.inventory.views import (
    InventoryDashboardView,
    StockAdjustmentCreateView,
    StockMovementListView,
)

app_name = "inventory"

urlpatterns = [
    path("", InventoryDashboardView.as_view(), name="dashboard"),
    path("movements/", StockMovementListView.as_view(), name="movement_list"),
    path("adjust/", StockAdjustmentCreateView.as_view(), name="adjust_stock"),
]
