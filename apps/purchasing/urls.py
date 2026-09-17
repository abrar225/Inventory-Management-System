from django.urls import path

from apps.purchasing.views import (
    PurchaseCreateView,
    PurchaseDetailView,
    PurchaseListView,
    PurchaseReceiveView,
)

app_name = "purchasing"

urlpatterns = [
    path("", PurchaseListView.as_view(), name="purchase_list"),
    path("add/", PurchaseCreateView.as_view(), name="purchase_add"),
    path("<uuid:pk>/", PurchaseDetailView.as_view(), name="purchase_detail"),
    path(
        "<uuid:pk>/receive/",
        PurchaseReceiveView.as_view(),
        name="purchase_receive",
    ),
]
