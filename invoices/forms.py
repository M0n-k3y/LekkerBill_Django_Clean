from django import forms
from decimal import Decimal
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'description', 'unit_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        # Add ID for Tom-select JavaScript
        self.fields['customer'].widget.attrs.update({'id': 'customer-select'})

        if user and hasattr(user, 'profile'):
            profile = user.profile
            default_tax = profile.vat_percentage
            tax_choices = [
                (Decimal('0.00'), 'None (0%)'),
                (default_tax, f'Default ({default_tax}%)')
            ]
            # If the default tax is 0, the list would have two identical '0.00' options.
            # This removes the duplicate 'Default (0%)' to keep the dropdown clean.
            if default_tax == Decimal('0.00'):
                tax_choices.pop()

            self.fields['tax_rate'] = forms.ChoiceField(choices=tax_choices, widget=forms.Select(attrs={'class': 'form-select'}))


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['customer', 'quote_date', 'status', 'tax_rate']
        widgets = {
            'quote_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        # Add ID for Tom-select JavaScript
        self.fields['customer'].widget.attrs.update({'id': 'customer-select'})

        if user and hasattr(user, 'profile'):
            profile = user.profile
            default_tax = profile.vat_percentage
            tax_choices = [
                (Decimal('0.00'), 'None (0%)'),
                (default_tax, f'Default ({default_tax}%)')
            ]
            # If the default tax is 0, the list would have two identical '0.00' options.
            # This removes the duplicate 'Default (0%)' to keep the dropdown clean.
            if default_tax == Decimal('0.00'):
                tax_choices.pop()

            self.fields['tax_rate'] = forms.ChoiceField(choices=tax_choices, widget=forms.Select(attrs={'class': 'form-select'}))


class InvoiceItemForm(forms.ModelForm):
    """A form for a single invoice line item, with Bootstrap styling."""
    class Meta:
        model = InvoiceItem
        fields = ['description', 'long_description', 'quantity', 'unit_price']
        widgets = {
            'long_description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: Add more details here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class QuoteItemForm(forms.ModelForm):
    """A form for a single quote line item, with Bootstrap styling."""
    class Meta:
        model = QuoteItem
        fields = ['description', 'long_description', 'quantity', 'unit_price']
        widgets = {
            'long_description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: Add more details here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})