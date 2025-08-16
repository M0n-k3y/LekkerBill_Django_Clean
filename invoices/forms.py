from django import forms
from .models import Customer, InventoryItem, Quote, Invoice, Profile, InvoiceItem, QuoteItem
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'description', 'unit_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProfileForm(forms.ModelForm):
    """Form for user-specific settings."""
    class Meta:
        model = Profile
        exclude = ['user'] # Let the view handle the user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the 'form-control' class to all visible fields for Bootstrap styling
        for field_name, field in self.fields.items():
            # The logo is a FileInput, which Bootstrap styles differently, so we skip it.
            if field_name != 'logo':
                field.widget.attrs.update({'class': 'form-control'})


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'invoice_date', 'due_date', 'status', 'tax_rate']
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['customer', 'quote_date', 'status', 'tax_rate']
        widgets = {
            'quote_date': forms.DateInput(attrs={'type': 'date'}),
        }