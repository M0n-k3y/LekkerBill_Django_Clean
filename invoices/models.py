from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
import uuid
from django.utils import timezone
from decimal import Decimal


class Customer(models.Model):
    """Represents a customer associated with a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Profile(models.Model):
    """Holds all user-specific settings and company details."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_branch_code = models.CharField(max_length=20, blank=True, null=True)
    bank_account_type = models.CharField(max_length=50, blank=True, null=True)
    invoice_prefix = models.CharField(max_length=10, default='INV-')
    invoice_next_number = models.IntegerField(default=1)
    quote_prefix = models.CharField(max_length=10, default='QTE-')
    quote_next_number = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.user.username} Profile'


class Subscription(models.Model):
    PLAN_CHOICES = (('free', 'Free'), ('pro', 'Pro'))
    STATUS_CHOICES = (('active', 'Active'), ('cancelled', 'Cancelled'), ('expired', 'Expired'))

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payfast_token = models.CharField(max_length=255, blank=True, null=True)
    subscription_start_date = models.DateField(default=timezone.now)
    subscription_end_date = models.DateField(blank=True, null=True)

    @property
    def is_currently_active(self):
        if self.plan == 'pro' and self.status == 'active' and self.subscription_end_date and self.subscription_end_date >= timezone.now().date():
            return True
        return False

    def __str__(self):
        return f"{self.user.username}'s {self.get_plan_display()} Subscription"


class InventoryItem(models.Model):
    """Represents a pre-defined product or service that can be quickly added to a quote or invoice."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    name = models.CharField(max_length=255, help_text="The name of the product or service.")
    description = models.TextField(blank=True, null=True, help_text="A description for internal reference.")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        ordering = ['name']


class Quote(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'), ('rejected', 'Rejected'))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotes')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='quotes')
    quote_number = models.CharField(max_length=50, blank=True, null=True)
    quote_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invoice = models.OneToOneField('Invoice', on_delete=models.SET_NULL, blank=True, null=True, related_name='converted_from_quote')

    @property
    def total(self):
        return self.subtotal + self.tax_amount

    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / Decimal(100))

    def get_absolute_url(self):
        """Returns the URL to access a particular quote instance."""
        return reverse('quote_detail', args=[str(self.id)])

    def get_public_url(self, request):
        """Returns the full public URL for the customer to view."""
        return request.build_absolute_uri(reverse('quote_public_view', args=[str(self.public_id)]))

    def __str__(self):
        return f"Quote {self.quote_number or self.id} for {self.customer.name}"


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    long_description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.description


class Invoice(models.Model):
    STATUS_CHOICES = (('proforma', 'Proforma'), ('unpaid', 'Unpaid'), ('paid', 'Paid'))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    @property
    def total(self):
        return self.subtotal + self.tax_amount

    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / Decimal(100))

    def get_absolute_url(self):
        """Returns the URL to access a particular invoice instance."""
        return reverse('invoice_detail', args=[str(self.id)])

    def __str__(self):
        return f"Invoice {self.invoice_number or self.id} for {self.customer.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    long_description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.description


@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    """Create Profile and Subscription for a new user."""
    if created:
        Profile.objects.create(user=instance)
        Subscription.objects.create(user=instance)


class Notification(models.Model):
    """Represents a notification for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True, help_text="A link to the relevant object (e.g., a quote).")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"