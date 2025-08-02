import uuid
from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # --- Company Information ---
    company_name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    #Company Address Details
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    # User-definable VAT rate
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'),
                                         help_text="Enter VAT as a percentage, e.g., 15.00")

    # --- Banking Details ---
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    # Account Holder Name
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_branch_code = models.CharField(max_length=50, blank=True, null=True)
    bank_account_type = models.CharField(max_length=50, blank=True, null=True,
                                         help_text="e.g., Cheque, Savings, Business")

    # Invoice & Quote Numbering Settings
    invoice_prefix = models.CharField(max_length=10, default='INV-', blank=True)
    invoice_next_number = models.PositiveIntegerField(default=1)
    quote_prefix = models.CharField(max_length=10, default='QUO-', blank=True)
    quote_next_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.user.username


class Subscription(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
    )

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    payfast_token = models.CharField(max_length=255, blank=True, null=True, unique=True,
                                     help_text="Unique token for the recurring billing agreement from PayFast.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active',
                              help_text="Status of the subscription.")
    subscription_end_date = models.DateField(blank=True, null=True,
                                             help_text="The date when the current subscription period ends.")

    def __str__(self):
        return f"{self.profile.user.username} - {self.get_plan_display()} Plan ({self.status})"

    @property
    def is_currently_active(self):

        if self.plan == 'pro' and self.status == 'active' and self.subscription_end_date:
            return self.subscription_end_date >= timezone.now().date()
        return False


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        Subscription.objects.create(profile=profile)
    if not created:
        instance.profile.save()


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('proforma', 'Proforma'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]
    invoice_number = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    # This now stores the tax rate for this specific invoice
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    due_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        # Use the new invoice number if it exists
        display_number = self.invoice_number or f"#{self.pk}"
        return f"Invoice {display_number} - {self.customer.name}"

    def get_absolute_url(self):
        return reverse('invoice_detail', kwargs={'invoice_id': self.id})

    @property
    def subtotal(self):
        return sum(item.total() for item in self.items.all())

    @property
    def tax_amount(self):
        # The rate is now a simple decimal, not a percentage string
        return self.subtotal * (self.tax_rate / 100)

    @property
    def total(self):
        return self.subtotal + self.tax_amount


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    long_description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} x {self.quantity}"

    def total(self):
        return self.quantity * self.unit_price


class Quote(models.Model):

    quote_number = models.CharField(max_length=50, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quote_date = models.DateField(default=timezone.now)
    valid_until = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='draft'
    )
    invoice = models.OneToOneField(
        'Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='converted_from_quote'
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        display_number = self.quote_number or f"#{self.pk}"
        return f"Quote {display_number} - {self.customer.name}"

    def get_absolute_url(self):
        return reverse('quote_detail', kwargs={'quote_id': self.id})

    @property
    def subtotal(self):
        return sum(item.total() for item in self.items.all())

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / 100)

    @property
    def total(self):
        return self.subtotal + self.tax_amount

    def is_converted(self):
        return self.invoice is not None


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    long_description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} x {self.quantity}"

    def total(self):
        return self.quantity * self.unit_price

# Inventory Items
class InventoryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text="The name of the product or service.")
    description = models.TextField(blank=True, null=True, help_text="A default description for the item.")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="The default price for one unit.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - R{self.unit_price}"

    class Meta:
        # Ensure that each user has unique item names
        unique_together = ('user', 'name')
        ordering = ['name']