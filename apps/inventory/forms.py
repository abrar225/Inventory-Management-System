from django import forms

from apps.catalog.models import Product
from apps.inventory.models import StockAdjustment

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
    """Apply CSS classes to form fields based on widget type."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.Select):
            widget.attrs["class"] = _SELECT_CLASS
        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = _TEXTAREA_CLASS
            widget.attrs.setdefault("rows", 3)
        else:
            widget.attrs["class"] = _TEXT_INPUT_CLASS


class StockAdjustmentForm(forms.ModelForm):
    """Form for manual inventory stock adjustments."""

    class Meta:
        model = StockAdjustment
        fields = ["product", "adjustment_type", "quantity", "reason"]
        widgets = {
            "quantity": forms.NumberInput(
                attrs={"placeholder": "Enter quantity", "min": "1"}
            ),
            "reason": forms.Textarea(
                attrs={"placeholder": "Describe the reason for adjustment..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit choices to active and alive products
        self.fields["product"].queryset = Product.objects.alive().filter(  # type: ignore[attr-defined]
            is_active=True
        )
        _style_fields(self)

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty is not None and qty <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return qty
