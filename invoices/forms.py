from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Customer,
    Invoice,
    InvoiceItem,
    Quote,
    QuoteItem,
    Profile,
    InventoryItem
)
from decimal import Decimal

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'subscription')
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_branch_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_type': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_next_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'quote_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'quote_next_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'invoice_date', 'due_date', 'status', 'tax_rate']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select', 'id': 'customer-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['customer'].queryset = Customer.objects.filter(user=user)

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['customer', 'quote_date', 'status', 'tax_rate']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select', 'id': 'customer-select'}),
            'quote_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['customer'].queryset = Customer.objects.filter(user=user)

# INVENTORY
class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'description', 'unit_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# --- Formsets ---
InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem,
    fields=('description', 'long_description', 'quantity', 'unit_price'),
    extra=1,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Description'}),
        'long_description': forms.Textarea(attrs={'class': 'form-control', 'rows': '1', 'placeholder': 'Additional details...'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Qty'}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Unit Price'}),
    }
)

QuoteItemFormSet = inlineformset_factory(
    Quote, QuoteItem,
    fields=('description', 'long_description', 'quantity', 'unit_price'),
    extra=1,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Description'}),
        'long_description': forms.Textarea(attrs={'class': 'form-control', 'rows': '1', 'placeholder': 'Additional details...'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Qty'}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Unit Price'}),
    }
)