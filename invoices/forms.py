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
        
        # Format the numbering fields to have leading zeros for display
        if self.instance:
            # We use TextInput to allow for the custom string format.
            # Django's ModelForm is smart enough to convert "0001" back to an integer 1 on save.
            self.fields['invoice_next_number'].widget = forms.TextInput(attrs={'class': 'form-control'})
            self.initial['invoice_next_number'] = f"{self.instance.invoice_next_number:04d}"

            self.fields['quote_next_number'].widget = forms.TextInput(attrs={'class': 'form-control'})
            self.initial['quote_next_number'] = f"{self.instance.quote_next_number:04d}"


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

            # Use a dictionary to build choices, ensuring unique keys (tax rates)
            # and controlling the labels. This prevents the tax rate from being
            # accidentally reset if the user's default tax changes.
            tax_choices_dict = {
                Decimal('0.00'): 'None (0%)'
            }

            # Add the default tax rate, formatted as a whole number
            tax_choices_dict[default_tax] = f'Default ({default_tax:.0f}%)'

            # If the instance has a tax rate that's not already in our choices, add it.
            if self.instance and self.instance.pk and self.instance.tax_rate is not None:
                current_tax = self.instance.tax_rate
                if current_tax not in tax_choices_dict:
                    tax_choices_dict[current_tax] = f'{current_tax:.0f}% (current)'

            # Convert the dictionary to a list of tuples and sort by the tax rate.
            sorted_tax_choices = sorted(tax_choices_dict.items())

            self.fields['tax_rate'] = forms.ChoiceField(
                choices=sorted_tax_choices,
                widget=forms.Select(attrs={'class': 'form-select'})
            )


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['customer', 'quote_date', 'valid_until', 'status', 'tax_rate']
        widgets = {
            'quote_date': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
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

            # Use a dictionary to build choices, ensuring unique keys (tax rates)
            # and controlling the labels. This prevents the tax rate from being
            # accidentally reset if the user's default tax changes.
            tax_choices_dict = {
                Decimal('0.00'): 'None (0%)'
            }

            # Add the default tax rate, formatted as a whole number
            tax_choices_dict[default_tax] = f'Default ({default_tax:.0f}%)'

            # If the instance has a tax rate that's not already in our choices, add it.
            if self.instance and self.instance.pk and self.instance.tax_rate is not None:
                current_tax = self.instance.tax_rate
                if current_tax not in tax_choices_dict:
                    tax_choices_dict[current_tax] = f'{current_tax:.0f}% (current)'

            # Convert the dictionary to a list of tuples and sort by the tax rate.
            sorted_tax_choices = sorted(tax_choices_dict.items())

            self.fields['tax_rate'] = forms.ChoiceField(
                choices=sorted_tax_choices,
                widget=forms.Select(attrs={'class': 'form-select'})
            )


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