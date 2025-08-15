from django.contrib import admin
from .models import Customer, Invoice, InvoiceItem, Quote, QuoteItem, Profile, Subscription
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html

# -------------------
# Invoice Admin Setup
# -------------------
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    # The following are not standard TabularInline attributes but are kept for reference
    # can_delete = True
    # show_change_link = True
    # verbose_name = "Invoice Line Item"
    # verbose_name_plural = "Invoice Line Items"

class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]
    # ✅ Use the new 'status' field instead of the old 'paid' field
    list_display = (
        'id', 'customer_name', 'invoice_date', 'due_date', 'status',
        'get_subtotal', 'get_tax', 'get_total', 'view_link', 'pdf_link'
    )

    def view_link(self, obj):
        url = reverse('invoice_detail', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">View</a>', url)
    view_link.short_description = 'View Invoice'

    def pdf_link(self, obj):
        url = reverse('invoice_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">PDF</a>', url)
    pdf_link.short_description = 'Download PDF'

    # ✅ Use 'status' here as well
    list_filter = ('status', 'tax_rate', 'user')
    search_fields = ('customer__name', 'id')
    autocomplete_fields = ['customer'] # Makes customer selection easier

    @admin.display(description='Customer Name', ordering='customer__name')
    def customer_name(self, obj):
        return obj.customer.name

    @admin.display(description='Subtotal')
    def get_subtotal(self, obj):
        return f"R{obj.subtotal:.2f}"

    @admin.display(description='Tax')
    def get_tax(self, obj):
        return f"R{obj.tax_amount:.2f}"

    @admin.display(description='Total')
    def get_total(self, obj):
        return f"R{obj.total:.2f}"

# -------------------
# Quote Admin Setup
# -------------------
class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1

class QuoteAdmin(admin.ModelAdmin):
    inlines = [QuoteItemInline]
    list_display = (
        'id', 'customer_name', 'quote_date', 'status',
        'get_total', 'is_converted', 'view_link'
    )
    list_filter = ('status', 'user')
    search_fields = ('customer__name', 'id')
    actions = ['convert_to_invoice_action']
    autocomplete_fields = ['customer']

    @admin.display(boolean=True, description='Converted?')
    def is_converted(self, obj):
        return obj.invoice is not None

    @admin.action(description="Convert selected accepted quotes to invoices")
    def convert_to_invoice_action(self, request, queryset):
        # Filter for quotes that are accepted and not yet converted
        eligible_quotes = queryset.filter(status='accepted', invoice__isnull=True)
        converted_count = 0
        for quote in eligible_quotes:
            # Re-using the logic from your view is a good idea.
            # For simplicity here, we'll just create the invoice.
            new_invoice = Invoice.objects.create(
                user=quote.user,
                customer=quote.customer,
                invoice_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=30),
                tax_rate=quote.tax_rate
            )
            for item in quote.items.all():
                InvoiceItem.objects.create(
                    invoice=new_invoice,
                    description=item.description,
                    long_description=item.long_description,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
            quote.invoice = new_invoice
            quote.save()
            converted_count += 1

        if converted_count:
            self.message_user(request, f"{converted_count} invoice(s) created successfully.")
        else:
            self.message_user(request, "No eligible quotes were converted. Make sure they are 'Accepted' and not already converted.", messages.WARNING)

    @admin.display(description='Customer Name', ordering='customer__name')
    def customer_name(self, obj):
        return obj.customer.name

    @admin.display(description='Total')
    def get_total(self, obj):
        return f"R{obj.total:.2f}"

    def view_link(self, obj):
        url = reverse('quote_detail', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">View</a>', url)
    view_link.short_description = 'View Quote'


# -------------------
# Other Admin Setups
# -------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'user')
    search_fields = ('name', 'email', 'user__username')
    list_filter = ('user',)

# -------------------
# Register Models
# -------------------
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Profile)
admin.site.register(Subscription)