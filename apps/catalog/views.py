from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.catalog.forms import CategoryForm, ProductForm, SupplierForm
from apps.catalog.models import Category, Product, Supplier
from apps.catalog.services import (
    CategoryService,
    ProductService,
    SupplierService,
)

# === Category Views ===

class CategoryListView(PermissionRequiredMixin, ListView):
    """List categories with search functionality."""

    model = Category
    template_name = "catalog/category_list.html"
    context_object_name = "categories"
    paginate_by = 10
    permission_required = "catalog.view_category"

    def get_queryset(self):
        # We query the alive categories (excluding soft-deleted ones)
        queryset = Category.objects.alive()
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context


class CategoryCreateView(PermissionRequiredMixin, CreateView):
    """Create a new category using CategoryService."""

    model = Category
    form_class = CategoryForm
    template_name = "catalog/category_form.html"
    success_url = reverse_lazy("catalog:category_list")
    permission_required = "catalog.add_category"

    def form_valid(self, form):
        CategoryService.create_category(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            is_active=form.cleaned_data["is_active"],
            created_by=self.request.user,
        )
        messages.success(self.request, "Category created successfully.")
        return redirect(self.success_url)


class CategoryUpdateView(PermissionRequiredMixin, UpdateView):
    """Update a category using CategoryService."""

    model = Category
    form_class = CategoryForm
    template_name = "catalog/category_form.html"
    success_url = reverse_lazy("catalog:category_list")
    permission_required = "catalog.change_category"

    def get_queryset(self):
        return Category.objects.alive()

    def form_valid(self, form):
        CategoryService.update_category(
            category=self.object,
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            is_active=form.cleaned_data["is_active"],
            updated_by=self.request.user,
        )
        messages.success(self.request, "Category updated successfully.")
        return redirect(self.success_url)


class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    """Soft-delete a category using CategoryService."""

    model = Category
    template_name = "catalog/category_confirm_delete.html"
    success_url = reverse_lazy("catalog:category_list")
    permission_required = "catalog.delete_category"

    def get_queryset(self):
        return Category.objects.alive()

    def form_valid(self, form):
        CategoryService.delete_category(self.object)
        messages.success(self.request, "Category deleted successfully (soft delete).")
        return redirect(self.success_url)


# === Supplier Views ===

class SupplierListView(PermissionRequiredMixin, ListView):
    """List suppliers with search functionality."""

    model = Supplier
    template_name = "catalog/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 10
    permission_required = "catalog.view_supplier"

    def get_queryset(self):
        queryset = Supplier.objects.alive()
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(company_name__icontains=q)
                | Q(contact_person__icontains=q)
                | Q(email__icontains=q)
                | Q(phone__icontains=q)
            )
        return queryset.order_by("company_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context


class SupplierCreateView(PermissionRequiredMixin, CreateView):
    """Create a new supplier using SupplierService."""

    model = Supplier
    form_class = SupplierForm
    template_name = "catalog/supplier_form.html"
    success_url = reverse_lazy("catalog:supplier_list")
    permission_required = "catalog.add_supplier"

    def form_valid(self, form):
        SupplierService.create_supplier(
            company_name=form.cleaned_data["company_name"],
            contact_person=form.cleaned_data["contact_person"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"],
            gst_number=form.cleaned_data.get("gst_number", ""),
            address=form.cleaned_data["address"],
            city=form.cleaned_data["city"],
            state=form.cleaned_data["state"],
            postal_code=form.cleaned_data["postal_code"],
            country=form.cleaned_data.get("country", "India"),
            notes=form.cleaned_data.get("notes", ""),
            is_active=form.cleaned_data["is_active"],
            created_by=self.request.user,
        )
        messages.success(self.request, "Supplier created successfully.")
        return redirect(self.success_url)


class SupplierUpdateView(PermissionRequiredMixin, UpdateView):
    """Update a supplier using SupplierService."""

    model = Supplier
    form_class = SupplierForm
    template_name = "catalog/supplier_form.html"
    success_url = reverse_lazy("catalog:supplier_list")
    permission_required = "catalog.change_supplier"

    def get_queryset(self):
        return Supplier.objects.alive()

    def form_valid(self, form):
        SupplierService.update_supplier(
            supplier=self.object,
            company_name=form.cleaned_data["company_name"],
            contact_person=form.cleaned_data["contact_person"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"],
            gst_number=form.cleaned_data.get("gst_number", ""),
            address=form.cleaned_data["address"],
            city=form.cleaned_data["city"],
            state=form.cleaned_data["state"],
            postal_code=form.cleaned_data["postal_code"],
            country=form.cleaned_data.get("country", "India"),
            notes=form.cleaned_data.get("notes", ""),
            is_active=form.cleaned_data["is_active"],
            updated_by=self.request.user,
        )
        messages.success(self.request, "Supplier updated successfully.")
        return redirect(self.success_url)


class SupplierDeleteView(PermissionRequiredMixin, DeleteView):
    """Soft-delete a supplier using SupplierService."""

    model = Supplier
    template_name = "catalog/supplier_confirm_delete.html"
    success_url = reverse_lazy("catalog:supplier_list")
    permission_required = "catalog.delete_supplier"

    def get_queryset(self):
        return Supplier.objects.alive()

    def form_valid(self, form):
        SupplierService.delete_supplier(self.object)
        messages.success(self.request, "Supplier deleted successfully (soft delete).")
        return redirect(self.success_url)


# === Product Views ===

class ProductListView(PermissionRequiredMixin, ListView):
    """List products with filtering and search capabilities."""

    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 10
    permission_required = "catalog.view_product"

    def get_queryset(self):
        queryset = Product.objects.alive().select_related("category", "supplier")
        q = self.request.GET.get("q")
        category_id = self.request.GET.get("category")
        supplier_id = self.request.GET.get("supplier")
        stock_status = self.request.GET.get("stock_status")

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(sku__icontains=q)
                | Q(barcode__icontains=q)
            )
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)

        # Filter by stock status if requested
        if stock_status == "low":
            queryset = queryset.filter(current_stock__lte=F("minimum_stock"))
        elif stock_status == "out":
            queryset = queryset.filter(current_stock__lte=0)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_supplier"] = self.request.GET.get("supplier", "")
        context["selected_stock_status"] = self.request.GET.get("stock_status", "")

        # Populate filter selections (active & not deleted only)
        context["categories"] = Category.objects.alive().filter(is_active=True).order_by("name")
        context["suppliers"] = Supplier.objects.alive().filter(is_active=True).order_by("company_name")
        return context


class ProductDetailView(PermissionRequiredMixin, DetailView):
    """Detailed view of a product."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    permission_required = "catalog.view_product"

    def get_queryset(self):
        return Product.objects.alive().select_related("category", "supplier")


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """Create a new product using ProductService."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:product_list")
    permission_required = "catalog.add_product"

    def form_valid(self, form):
        ProductService.create_product(
            sku=form.cleaned_data["sku"],
            name=form.cleaned_data["name"],
            category=form.cleaned_data["category"],
            supplier=form.cleaned_data["supplier"],
            purchase_price=form.cleaned_data["purchase_price"],
            selling_price=form.cleaned_data["selling_price"],
            barcode=form.cleaned_data.get("barcode"),
            minimum_stock=form.cleaned_data.get("minimum_stock", 5),
            unit=form.cleaned_data.get("unit", "PCS"),
            description=form.cleaned_data.get("description", ""),
            image=form.cleaned_data.get("image"),
            is_active=form.cleaned_data["is_active"],
            created_by=self.request.user,
        )
        messages.success(self.request, "Product created successfully.")
        return redirect(self.success_url)


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    """Update a product using ProductService."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:product_list")
    permission_required = "catalog.change_product"

    def get_queryset(self):
        return Product.objects.alive()

    def form_valid(self, form):
        ProductService.update_product(
            product=self.object,
            sku=form.cleaned_data["sku"],
            name=form.cleaned_data["name"],
            category=form.cleaned_data["category"],
            supplier=form.cleaned_data["supplier"],
            purchase_price=form.cleaned_data["purchase_price"],
            selling_price=form.cleaned_data["selling_price"],
            barcode=form.cleaned_data.get("barcode"),
            minimum_stock=form.cleaned_data.get("minimum_stock", 5),
            unit=form.cleaned_data.get("unit", "PCS"),
            description=form.cleaned_data.get("description", ""),
            image=form.cleaned_data.get("image"),
            is_active=form.cleaned_data["is_active"],
            updated_by=self.request.user,
        )
        messages.success(self.request, "Product updated successfully.")
        return redirect(self.success_url)


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    """Soft-delete a product using ProductService."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:product_list")
    permission_required = "catalog.delete_product"

    def get_queryset(self):
        return Product.objects.alive()

    def form_valid(self, form):
        ProductService.delete_product(self.object)
        messages.success(self.request, "Product deleted successfully (soft delete).")
        return redirect(self.success_url)
