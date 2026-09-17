from django import forms
from django.forms import inlineformset_factory

from apps.catalog.models import Product
from apps.purchasing.models import Purchase, PurchaseItem

_TEXT_INPUT_CLASS = (
    "h-12 w-full rounded-xl border border-border bg-surface px-md "
    "text-body text-text-primary placeholder:text-text-secondary "
    "focus:border-primary focus:outline-none focus:ring-2 "
    "focus:ring-primary/30 dark:border-dark-border dark:bg-dark-surface "
    "dark:text-dark-text"
)

_SELECT_CLASS = (
    "h-12 w-full rounded-xl border border-border bg-surface px-md "
    "text-body text-text-primary focus:border-primary focus:outline-none "
    "focus:ring-2 focus:ring-primary/30 dark:border-dark-border "
    "dark:bg-dark-surface dark:text-dark-text"
)

_TEXTAREA_CLASS = (
    "w-full rounded-xl border border-border bg-surface p-md text-body "
    "text-text-primary placeholder:text-text-secondary focus:border-primary "
    "focus:outline-none focus:ring-2 focus:ring-primary/30 "
    "dark:border-dark-border dark:bg-dark-surface dark:text-dark-text"
)


def _style_fields(form: forms.BaseForm) -> None:
    """Applies standardized style token CSS classes to form inputs."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.Select):
            widget.attrs["class"] = _SELECT_CLASS
        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = _TEXTAREA_CLASS
            widget.attrs.setdefault("rows", 3)
        else:
            widget.attrs["class"] = _TEXT_INPUT_CLASS


class PurchaseForm(forms.ModelForm):
    """Parent Purchase Order attributes form."""

    class Meta:
        model = Purchase
        fields = ["supplier", "purchase_date", "tax", "discount", "notes"]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "tax": forms.NumberInput(attrs={"placeholder": "0.00", "step": "0.01"}),
            "discount": forms.NumberInput(
                attrs={"placeholder": "0.00", "step": "0.01"}
            ),
            "notes": forms.Textarea(
                attrs={"placeholder": "Optional special references or notes..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class PurchaseItemForm(forms.ModelForm):
    """Line item sub-form for Purchase Orders."""

    class Meta:
        model = PurchaseItem
        fields = ["product", "quantity", "unit_price"]
        widgets = {
            "quantity": forms.NumberInput(
                attrs={"placeholder": "1", "min": "1", "class": "qty-field"}
            ),
            "unit_price": forms.NumberInput(
                attrs={"placeholder": "0.00", "step": "0.01", "class": "price-field"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.alive().filter(  # type: ignore[attr-defined]
            is_active=True
        )
        _style_fields(self)


PurchaseItemFormSet = inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
)
