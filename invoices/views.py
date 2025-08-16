from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.forms import inlineformset_factory
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from weasyprint import HTML
from .forms import SignUpForm, CustomerForm, InventoryItemForm, ProfileForm, InvoiceForm, QuoteForm, InvoiceItemForm, QuoteItemForm
from .models import Customer, Quote, Invoice, Subscription, InventoryItem, Profile, InvoiceItem, QuoteItem, Notification

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    # Ensure subscription exists, creating it if necessary.
    # This is a robust way to handle users created before the subscription model was added.
    subscription, created = Subscription.objects.get_or_create(user=request.user)

    # ✅ This now uses real data from your database.
    # We use `select_related` to efficiently fetch the customer's name
    # along with the invoice/quote, avoiding extra database queries.
    context = {
        'customer_count': Customer.objects.filter(user=request.user).count(),
        'quote_count': Quote.objects.filter(user=request.user).count(),
        'invoice_count': Invoice.objects.filter(user=request.user).count(),
        'recent_invoices': Invoice.objects.filter(user=request.user)
                                        .select_related('customer')
                                        .order_by('-invoice_date')[:5],
        'recent_quotes': Quote.objects.filter(user=request.user)
                                      .select_related('customer')
                                      .order_by('-quote_date')[:5],
        'subscription': subscription
    }
    return render(request, 'invoices/dashboard.html', context)

# --- Customer CRUD Views ---

@login_required
def customer_list(request):
    customers = Customer.objects.filter(user=request.user)
    return render(request, 'invoices/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            messages.success(request, f"Customer '{customer.name}' created successfully.")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'invoices/customer_form.html', {'form': form, 'title': 'Create New Customer'})

@login_required
def customer_update(request, pk):
    customer = Customer.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.name}' updated successfully.")
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'invoices/customer_form.html', {'form': form, 'title': f'Edit {customer.name}'})

@login_required
def customer_delete(request, pk):
    customer = Customer.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        customer_name = customer.name
        customer.delete()
        messages.success(request, f"Customer '{customer_name}' has been deleted.")
        return redirect('customer_list')
    return render(request, 'invoices/customer_confirm_delete.html', {'customer': customer})

# --- Inventory CRUD Views ---

@login_required
def inventory_list(request):
    inventory_items = InventoryItem.objects.filter(user=request.user)
    context = {
        'inventory_items': inventory_items,
        'title': 'Inventory Items' # The template uses this title variable
    }
    return render(request, 'invoices/inventory_list.html', context)

@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f"Inventory item '{item.name}' created.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'invoices/inventory_form.html', {'form': form, 'title': 'Create New Inventory Item'})

@login_required
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Inventory item '{item.name}' updated.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'invoices/inventory_form.html', {'form': form, 'title': f'Edit {item.name}'})

@login_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f"Inventory item '{item_name}' has been deleted.")
        return redirect('inventory_list')
    return render(request, 'invoices/inventory_confirm_delete.html', {'item': item})

# --- Invoice CRUD Views ---

@login_required
def invoice_list(request):
    invoices = Invoice.objects.filter(user=request.user)
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    public_share_url = request.build_absolute_uri(invoice.get_absolute_url())
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice, 'public_share_url': public_share_url})

@login_required
def invoice_create(request):
    first_customer = Customer.objects.filter(user=request.user).first()
    if not first_customer:
        messages.warning(request, "You must create a customer before you can create an invoice.")
        return redirect('customer_create')

    # Default due date is 30 days from now, which is required by the model.
    due_date = timezone.now().date() + timedelta(days=30)

    invoice = Invoice.objects.create(user=request.user, customer=first_customer, due_date=due_date)
    messages.info(request, "New invoice draft created. You can now add items and details.")
    return redirect('invoice_update', pk=invoice.pk)

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice, prefix='items')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Invoice saved successfully.")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        form.fields['customer'].queryset = Customer.objects.filter(user=request.user) # Scope customers to the user
        formset = InvoiceItemFormSet(instance=invoice, prefix='items')

    context = {
        'form': form,
        'formset': formset,
        'title': f'Edit Invoice {invoice.invoice_number or invoice.id}',
        'inventory_items': InventoryItem.objects.filter(user=request.user)
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, "Invoice has been deleted.")
        return redirect('invoice_list')
    return render(request, 'invoices/invoice_confirm_delete.html', {'invoice': invoice})

# --- Quote CRUD Views ---

@login_required
def quote_list(request):
    quotes = Quote.objects.filter(user=request.user)
    return render(request, 'invoices/quote_list.html', {'quotes': quotes})

@login_required
def quote_detail(request, pk):
    quote = get_object_or_404(Quote, pk=pk, user=request.user)
    # Build the full public URL for sharing using the new method
    public_share_url = quote.get_public_url(request)
    return render(request, 'invoices/quote_detail.html', {'quote': quote, 'public_share_url': public_share_url})

@login_required
def quote_create(request):
    first_customer = Customer.objects.filter(user=request.user).first()
    if not first_customer:
        messages.warning(request, "You must create a customer before you can create a quote.")
        return redirect('customer_create')

    quote = Quote.objects.create(user=request.user, customer=first_customer)
    messages.info(request, "New quote draft created. You can now add items and details.")
    return redirect('quote_update', pk=quote.pk)

@login_required
def quote_update(request, pk):
    quote = get_object_or_404(Quote, pk=pk, user=request.user)
    QuoteItemFormSet = inlineformset_factory(Quote, QuoteItem, form=QuoteItemForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        formset = QuoteItemFormSet(request.POST, instance=quote, prefix='items')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Quote saved successfully.")
            return redirect('quote_detail', pk=quote.pk)
    else:
        form = QuoteForm(instance=quote)
        form.fields['customer'].queryset = Customer.objects.filter(user=request.user)
        formset = QuoteItemFormSet(instance=quote, prefix='items')

    context = {
        'form': form,
        'formset': formset,
        'title': f'Edit Quote {quote.quote_number or quote.id}',
        'inventory_items': InventoryItem.objects.filter(user=request.user)
    }
    return render(request, 'invoices/quote_form.html', context)

@login_required
def quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk, user=request.user)
    if request.method == 'POST':
        quote.delete()
        messages.success(request, "Quote has been deleted.")
        return redirect('quote_list')
    return render(request, 'invoices/quote_confirm_delete.html', {'quote': quote})


def quote_public_view(request, public_id):
    """A public view for a customer to see their quote."""
    quote = get_object_or_404(Quote, public_id=public_id)
    # We pass the profile of the user who CREATED the quote
    profile = quote.user.profile
    context = {
        'quote': quote,
        'profile': profile,
    }
    return render(request, 'invoices/quote_public.html', context)


def quote_customer_action(request, public_id):
    """Handles the customer accepting or rejecting the quote."""
    quote = get_object_or_404(Quote, public_id=public_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept' and quote.status in ['draft', 'sent']:
            quote.status = 'accepted'
            quote.save()
            # Create a notification for the business owner
            Notification.objects.create(
                user=quote.user,
                message=f"Quote #{quote.quote_number or quote.id} for {quote.customer.name} has been accepted.",
                link=quote.get_absolute_url()
            )
        elif action == 'reject' and quote.status in ['draft', 'sent']:
            quote.status = 'rejected'
            quote.save()
            # Create a notification for the business owner
            Notification.objects.create(
                user=quote.user,
                message=f"Quote #{quote.quote_number or quote.id} for {quote.customer.name} has been rejected.",
                link=quote.get_absolute_url()
            )
    return redirect('quote_public_view', public_id=quote.public_id)

@login_required
def convert_quote_to_invoice(request, pk):
    quote = get_object_or_404(Quote, pk=pk, user=request.user)
    if quote.invoice:
        messages.warning(request, "This quote has already been converted to an invoice.")
        return redirect('invoice_detail', pk=quote.invoice.pk)

    new_invoice = Invoice.objects.create(
        user=quote.user,
        customer=quote.customer,
        invoice_date=timezone.now().date(),
        due_date=timezone.now().date() + timedelta(days=30),
        tax_rate=quote.tax_rate,
        status='unpaid'
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
    quote.status = 'accepted'
    quote.save()
    messages.success(request, f"Quote {quote.id} successfully converted to Invoice {new_invoice.id}.")
    return redirect('invoice_update', pk=new_invoice.pk)

# --- Notifications ---

@login_required
def mark_notifications_as_read(request):
    """Marks all unread notifications for the current user as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def profile_view(request):
    """Displays the user's profile hub page."""
    return render(request, 'invoices/profile.html', {'title': 'My Profile'})

# --- Settings & Subscription ---

@login_required
def settings_update(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your settings have been updated.")
            return redirect('settings_update')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'invoices/settings_form.html', {'form': form, 'title': 'My Settings'})

@login_required
def subscription_detail(request):
    # Ensure subscription exists, creating it if necessary.
    subscription, created = Subscription.objects.get_or_create(user=request.user)

    # This context is needed for the template's logic
    context = {
        'subscription': subscription,
        'title': 'My Subscription',
        'invoice_count': Invoice.objects.filter(user=request.user).count(),
        'quote_count': Quote.objects.filter(user=request.user).count(),
        'customer_count': Customer.objects.filter(user=request.user).count(),
        # Pass settings constants to the template
        'settings': {'FREE_PLAN_ITEM_LIMIT': settings.FREE_PLAN_ITEM_LIMIT},
        'pro_plan_price': settings.PRO_PLAN_PRICE,
    }
    return render(request, 'invoices/subscription_detail.html', context)

@login_required
def upgrade_to_pro(request):
    # In a real app, this would redirect to PayFast
    messages.info(request, "PayFast integration is the next step!")
    return redirect('subscription_detail')

@login_required
def cancel_subscription(request):
    messages.info(request, "Subscription management is coming soon.")
    return redirect('subscription_detail')

@login_required
def reactivate_subscription(request):
    messages.info(request, "Subscription management is coming soon.")
    return redirect('subscription_detail')

# --- PDF & PWA Views ---

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    html_string = render_to_string('invoices/invoice_pdf.html', {'invoice': invoice, 'profile': request.user.profile})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice-{invoice.invoice_number or invoice.id}.pdf"'
    return response

@login_required
def quote_pdf(request, pk):
    quote = get_object_or_404(Quote, pk=pk, user=request.user)
    html_string = render_to_string('invoices/quote_pdf.html', {'quote': quote, 'profile': request.user.profile})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quote-{quote.quote_number or quote.id}.pdf"'
    return response

# --- PWA Views ---

def service_worker(request):
    """
    Serves the service-worker.js file.
    """
    return render(request, 'serviceworker.js', content_type='application/javascript')