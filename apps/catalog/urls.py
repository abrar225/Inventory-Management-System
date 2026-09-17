from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category_add"),
    path("categories/<uuid:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<uuid:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Suppliers
    path("suppliers/", views.SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/add/", views.SupplierCreateView.as_view(), name="supplier_add"),
    path("suppliers/<uuid:pk>/edit/", views.SupplierUpdateView.as_view(), name="supplier_edit"),
    path("suppliers/<uuid:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),

    # Products
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/add/", views.ProductCreateView.as_view(), name="product_add"),
    path("products/<uuid:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("products/<uuid:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("products/<uuid:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
]
