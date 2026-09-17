from django import forms

from apps.catalog.models import Category, Product, Supplier

_TEXT_INPUT_CLASS = (
    "h-12 w-full rounded-xl border border-border bg-surface px-md "
    "text-body text-text-primary placeholder:text-text-secondary "
    "focus:border-primary focus:outline-none focus:ring-2 "
    "focus:ring-primary/30 dark:border-dark-border dark:bg-dark-surface "
    "dark:text-dark-text"
)

_TEXTAREA_CLASS = (
    "w-full rounded-xl border border-border bg-surface px-md py-sm "
    "text-body text-text-primary placeholder:text-text-secondary "
    "focus:border-primary focus:outline-none focus:ring-2 "
    "focus:ring-primary/30 dark:border-dark-border dark:bg-dark-surface "
    "dark:text-dark-text"
)

_SELECT_CLASS = (
    "h-12 w-full rounded-xl border border-border bg-surface px-md "
    "text-body text-text-primary "
    "focus:border-primary focus:outline-none focus:ring-2 "
    "focus:ring-primary/30 dark:border-dark-border dark:bg-dark-surface "
    "dark:text-dark-text"
)

_CHECKBOX_CLASS = (
    "h-5 w-5 rounded border-border text-primary focus:ring-primary "
    "dark:border-dark-border"
)


def _style_fields(form: forms.BaseForm) -> None:
    """Apply CSS classes to form fields based on widget type."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = _CHECKBOX_CLASS
        elif isinstance(widget, forms.Select):
            widget.attrs["class"] = _SELECT_CLASS
        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = _TEXTAREA_CLASS
            widget.attrs.setdefault("rows", 3)
        elif isinstance(widget, forms.FileInput):
            # Styling for file input is done partially in the template, but we add a base class
            widget.attrs["class"] = "block w-full text-small text-text-secondary file:mr-md file:py-sm file:px-md file:rounded-xl file:border-0 file:text-small file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 dark:text-dark-text"
        else:
            widget.attrs["class"] = _TEXT_INPUT_CLASS


class CategoryForm(forms.ModelForm):
    """Form for Category CRUD."""

    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Category Name"}),
            "description": forms.Textarea(attrs={"placeholder": "Write category details..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class SupplierForm(forms.ModelForm):
    """Form for Supplier CRUD."""

    class Meta:
        model = Supplier
        fields = [
            "company_name",
            "contact_person",
            "email",
            "phone",
            "gst_number",
            "address",
            "city",
            "state",
            "postal_code",
            "country",
            "notes",
            "is_active",
        ]
        widgets = {
            "company_name": forms.TextInput(attrs={"placeholder": "ACME Corp"}),
            "contact_person": forms.TextInput(attrs={"placeholder": "John Doe"}),
            "email": forms.EmailInput(attrs={"placeholder": "supplier@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 99999 99999"}),
            "gst_number": forms.TextInput(attrs={"placeholder": "GSTIN (optional)"}),
            "address": forms.Textarea(attrs={"placeholder": "123 Business St..."}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "state": forms.TextInput(attrs={"placeholder": "State"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "Pin Code"}),
            "country": forms.TextInput(attrs={"placeholder": "Country"}),
            "notes": forms.Textarea(attrs={"placeholder": "Additional notes..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class ProductForm(forms.ModelForm):
    """Form for Product CRUD."""

    class Meta:
        model = Product
        fields = [
            "sku",
            "barcode",
            "name",
            "category",
            "supplier",
            "purchase_price",
            "selling_price",
            "minimum_stock",
            "unit",
            "description",
            "image",
            "is_active",
        ]
        widgets = {
            "sku": forms.TextInput(attrs={"placeholder": "PROD-1001"}),
            "barcode": forms.TextInput(attrs={"placeholder": "Barcode number (optional)"}),
            "name": forms.TextInput(attrs={"placeholder": "Product Name"}),
            "purchase_price": forms.NumberInput(attrs={"placeholder": "0.00", "step": "0.01"}),
            "selling_price": forms.NumberInput(attrs={"placeholder": "0.00", "step": "0.01"}),
            "minimum_stock": forms.NumberInput(attrs={"placeholder": "5"}),
            "unit": forms.TextInput(attrs={"placeholder": "PCS, BOX, KG..."}),
            "description": forms.Textarea(attrs={"placeholder": "Product details..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit foreign key choices to active ones (if adding new, or updating)
        self.fields["category"].queryset = Category.objects.alive().filter(is_active=True)  # type: ignore[attr-defined]
        self.fields["supplier"].queryset = Supplier.objects.alive().filter(is_active=True)  # type: ignore[attr-defined]
        _style_fields(self)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            purchase_price = cleaned_data.get("purchase_price")
            selling_price = cleaned_data.get("selling_price")

            if purchase_price is not None and selling_price is not None:
                if selling_price < purchase_price:
                    self.add_error(
                        "selling_price",
                        "Selling price must be greater than or equal to purchase price."
                    )
        return cleaned_data
