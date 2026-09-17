from django.urls import path

from apps.reporting.views import (
    InventoryValuationCSVExportView,
    PurchaseReportCSVExportView,
    ReportsDashboardView,
    SalesReportCSVExportView,
)

app_name = "reporting"

urlpatterns = [
    path("", ReportsDashboardView.as_view(), name="dashboard"),
    path(
        "inventory/csv/",
        InventoryValuationCSVExportView.as_view(),
        name="inventory_csv",
    ),
    path("sales/csv/", SalesReportCSVExportView.as_view(), name="sales_csv"),
    path(
        "purchases/csv/",
        PurchaseReportCSVExportView.as_view(),
        name="purchases_csv",
    ),
]
