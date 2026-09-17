from django.contrib import admin

from apps.catalog.models import Category, Product, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "is_deleted", "created_at")
    list_filter = ("is_active", "is_deleted")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_person", "email", "phone", "is_active", "is_deleted")
    list_filter = ("is_active", "is_deleted")
    search_fields = ("company_name", "contact_person", "email", "phone")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "name",
        "category",
        "supplier",
        "purchase_price",
        "selling_price",
        "current_stock",
        "is_active",
        "is_deleted",
    )
    list_filter = ("is_active", "is_deleted", "category", "supplier")
    search_fields = ("sku", "barcode", "name", "description")
    prepopulated_fields = {"slug": ("name",)}
