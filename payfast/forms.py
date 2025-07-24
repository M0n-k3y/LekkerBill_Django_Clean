# F:/Python Apps/LekkerBill_Django_Clean/payfast/forms.py

from django import forms

class PayFastForm(forms.Form):
    """
    A form to render the hidden fields for the PayFast payment gateway.
    This is a clean, minimal implementation controlled entirely by our project.
    """
    def __init__(self, *args, **kwargs):
        self.testing = kwargs.pop('testing', False)
        super().__init__(*args, **kwargs)

        # Create a hidden field for each piece of data from the view
        for field_name, field_value in self.initial.items():
            self.fields[field_name] = forms.CharField(initial=field_value, widget=forms.HiddenInput())

    def get_action(self):
        """Returns the correct PayFast URL based on the testing mode."""
        if self.testing:
            return "https://sandbox.payfast.co.za/eng/process"
        return "https://www.payfast.co.za/eng/process"