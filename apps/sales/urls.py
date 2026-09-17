from django.urls import path

from apps.sales.views import SaleCreateView, SaleDetailView, SaleListView

app_name = "sales"

urlpatterns = [
    path("", SaleListView.as_view(), name="sale_list"),
    path("add/", SaleCreateView.as_view(), name="sale_add"),
    path("<uuid:pk>/", SaleDetailView.as_view(), name="sale_detail"),
]
