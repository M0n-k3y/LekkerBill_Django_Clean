from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from django.db.models import Count
from django.conf import settings
from django.urls import reverse
from django.db import transaction
from .models import Invoice, Quote, InvoiceItem, QuoteItem, Customer, Profile, Subscription,  InventoryItem
from .forms import InvoiceForm, QuoteForm, InvoiceItemFormSet, QuoteItemFormSet, CustomerForm, SignUpForm, ProfileForm, InventoryItemForm
from django.contrib.auth.decorators import login_required
from functools import wraps
from payfast.forms import PayFastForm


def landing_page(request):
    """Displays the public landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'invoices/landing_page.html')


# --- Custom Decorators ---

def check_subscription_limit(model_name):
    """
    A decorator to check if a user on a free plan has reached their monthly creation limit.
    `model_name` should be 'invoice', 'quote', or 'customer'.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.profile.subscription.is_currently_active:
                today = timezone.now()
                start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                model_map = {'invoice': Invoice, 'quote': Quote, 'customer': Customer}
                model = model_map.get(model_name)
                if model:
                    limit = getattr(settings, 'FREE_PLAN_ITEM_LIMIT', 5)
                    count = model.objects.filter(user=request.user, created_at__gte=start_of_month).count()
                    if count >= limit:
                        messages.warning(request,
                                         f"You have reached your monthly limit of {limit} {model_name}s. Please upgrade to create more.")
                        return redirect('subscription_detail')
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# --- Authentication Views ---

def signup(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def settings_update(request):
    """Handles updating the user's profile and settings."""
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your settings have been updated successfully!')
            return redirect('settings_update')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'invoices/settings_form.html', {'form': form, 'title': 'Settings'})


# --- Subscription and Payment Views ---

@login_required
def subscription_detail(request):
    """Displays the user's current subscription plan and usage."""
    subscription = request.user.profile.subscription
    context = {
        'title': 'My Subscription',
        'subscription': subscription,
        'pro_plan_price': settings.PRO_PLAN_PRICE,
    }
    if not subscription.is_currently_active:
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        invoice_count = Invoice.objects.filter(user=request.user, created_at__gte=start_of_month).count()
        quote_count = Quote.objects.filter(user=request.user, created_at__gte=start_of_month).count()
        customer_count = Customer.objects.filter(user=request.user, created_at__gte=start_of_month).count()
        context.update({
            'invoice_count': invoice_count,
            'quote_count': quote_count,
            'customer_count': customer_count,
        })
    return render(request, 'invoices/subscription_detail.html', context)


@login_required
def upgrade_to_pro(request):
    """Prepares and redirects the user to PayFast to set up a recurring subscription."""
    subscription = request.user.profile.subscription
    if subscription.is_currently_active and subscription.plan == 'pro':
        messages.info(request, "You already have an active Pro subscription.")
        return redirect('subscription_detail')

    payfast_data = {
        'merchant_id': settings.PAYFAST_MERCHANT_ID,
        'merchant_key': settings.PAYFAST_MERCHANT_KEY,
        'return_url': request.build_absolute_uri(reverse('payment_success')),
        'cancel_url': request.build_absolute_uri(reverse('payment_cancel')),
        'notify_url': request.build_absolute_uri(reverse('payfast:payfast_notify_url')),
        'm_payment_id': subscription.id,
        # ✅ CHANGE THIS LINE: Explicitly format the amount
        'amount': f"{settings.PRO_PLAN_PRICE:.2f}",
        'item_name': f'LekkerBill Pro Monthly Subscription (R{settings.PRO_PLAN_PRICE})',
        'item_description': 'Unlock unlimited invoices, quotes, and customers.',
        'name_first': request.user.first_name or '',
        'name_last': request.user.last_name or '',
        'email_address': request.user.email,
        'subscription_type': '1',
        'frequency': '3',
        'cycles': '0'
    }

    form = PayFastForm(initial=payfast_data, testing=settings.PAYFAST_TESTING)
    context = {
        'form': form,
        'title': 'Redirecting to PayFast for Pro Subscription',
        'payfast_url': form.get_action()
    }
    return render(request, 'invoices/payfast_redirect.html', context)


@login_required
def payment_success(request):
    """Handles the user being redirected back after a successful payment."""
    messages.success(request, "Your payment was successful! Your subscription will be activated shortly.")
    return redirect('subscription_detail')


@login_required
def payment_cancel(request):
    """Handles the user cancelling the payment process."""
    messages.warning(request, "Your payment was cancelled. Your subscription has not been changed.")
    return redirect('subscription_detail')


@login_required
def cancel_subscription(request):
    """Handles a user's request to cancel their recurring subscription."""
    if request.method == 'POST':
        subscription = request.user.profile.subscription
        if subscription.plan == 'pro' and subscription.status == 'active':
            subscription.status = 'cancelled'
            subscription.save()
            messages.success(request,
                             "Your subscription has been cancelled. You will retain Pro access until the end of your current billing period.")
        else:
            messages.error(request, "No active subscription to cancel.")
        return redirect('subscription_detail')
    return redirect('subscription_detail')


@login_required
def reactivate_subscription(request):
    """Handles a user's request to reactivate a previously cancelled subscription."""
    if request.method == 'POST':
        subscription = request.user.profile.subscription
        if subscription.plan == 'pro' and subscription.status == 'cancelled':
            subscription.status = 'active'
            subscription.save()
            messages.success(request,
                             "Your subscription has been reactivated. It will now renew automatically at the end of the billing period.")
        else:
            messages.error(request, "No cancelled subscription to reactivate.")
        return redirect('subscription_detail')
    return redirect('subscription_detail')


# --- Dashboard ---

@login_required
def dashboard(request):
    """Displays the main dashboard with summary counts and recent activity."""
    user = request.user
    counts = user.customer_set.aggregate(
        customer_count=Count('id', distinct=True),
        invoice_count=Count('invoice', distinct=True),
        quote_count=Count('quote', distinct=True)
    )
    recent_invoices = Invoice.objects.filter(user=user).select_related('customer').order_by('-invoice_date',
                                                                                            '-created_at')[:5]
    recent_quotes = Quote.objects.filter(user=user).select_related('customer').order_by('-quote_date', '-created_at')[
                    :5]
    context = {
        'invoice_count': counts.get('invoice_count', 0),
        'quote_count': counts.get('quote_count', 0),
        'customer_count': counts.get('customer_count', 0),
        'recent_invoices': recent_invoices,
        'recent_quotes': recent_quotes,
        'subscription': user.profile.subscription,
    }
    return render(request, 'invoices/dashboard.html', context)


# --- Create, Update, Delete Views ---

@login_required
@check_subscription_limit('invoice')
def invoice_create(request):
    """Handles the creation of a new invoice with line items."""
    profile = request.user.profile

    if request.method == 'POST':
        form = InvoiceForm(request.POST, user=request.user)
        formset = InvoiceItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Lock the profile to prevent two invoices getting the same number
                profile_locked = Profile.objects.select_for_update().get(pk=profile.id)

                invoice = form.save(commit=False)
                invoice.user = request.user

                # --- Generate Custom Invoice Number ---
                year = timezone.now().year
                number = profile_locked.invoice_next_number
                invoice.invoice_number = f"{profile_locked.invoice_prefix}{year}/{number:06d}"
                invoice.save()

                # Increment the next number for the profile
                profile_locked.invoice_next_number += 1
                profile_locked.save()

                formset.instance = invoice
                formset.save()
                messages.success(request, f"Successfully created Invoice {invoice.invoice_number}")
                return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        # Pre-fill the form with the user's default VAT rate
        form = InvoiceForm(user=request.user, initial={'tax_rate': profile.vat_percentage})
        formset = InvoiceItemFormSet(prefix='items', queryset=InvoiceItem.objects.none())

    inventory_items = InventoryItem.objects.filter(user=request.user)

    context = {
        'form': form,
        'formset': formset,
        'title': 'Create a New Invoice',
        'inventory_items': inventory_items,
    }
    return render(request, 'invoices/invoice_form.html', context)


@login_required
def invoice_update(request, invoice_id):
    """Handles updating an existing invoice with line items."""
    invoice = get_object_or_404(Invoice, pk=invoice_id, user=request.user)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, user=request.user)
        formset = InvoiceItemFormSet(request.POST, instance=invoice, prefix='items')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm(instance=invoice, user=request.user)
        formset = InvoiceItemFormSet(instance=invoice, prefix='items')
    inventory_items = InventoryItem.objects.filter(user=request.user)
    context = {
        'form': form,
        'formset': formset,
        'title': f'Edit Invoice {invoice.invoice_number or f"#{invoice.id}"}',
        'inventory_items': inventory_items, # ✅ ADD THIS
    }
    return render(request, 'invoices/invoice_form.html', context)


@login_required
def invoice_delete(request, invoice_id):
    """Handles deleting an invoice after confirmation."""
    invoice = get_object_or_404(Invoice, pk=invoice_id, user=request.user)
    if request.method == 'POST':
        invoice_str = str(invoice)
        invoice.delete()
        messages.success(request, f"Successfully deleted {invoice_str}.")
        return redirect('invoice_list')
    context = {'object': invoice, 'form_type': 'Invoice'}
    return render(request, 'invoices/generic_confirm_delete.html', context)


@login_required
@check_subscription_limit('quote')
def quote_create(request):
    """Handles the creation of a new quote with line items."""
    profile = request.user.profile

    if request.method == 'POST':
        form = QuoteForm(request.POST, user=request.user)
        formset = QuoteItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                profile_locked = Profile.objects.select_for_update().get(pk=profile.id)

                quote = form.save(commit=False)
                quote.user = request.user

                # --- Generate Custom Quote Number ---
                year = timezone.now().year
                number = profile_locked.quote_next_number
                quote.quote_number = f"{profile_locked.quote_prefix}{year}/{number:06d}"
                quote.save()

                # Increment the next number for the profile
                profile_locked.quote_next_number += 1
                profile_locked.save()

                formset.instance = quote
                formset.save()
                messages.success(request, f"Successfully created Quote {quote.quote_number}")
                return redirect('quote_detail', quote_id=quote.id)
    else:
        # Pre-fill the form with the user's default VAT rate
        form = QuoteForm(user=request.user, initial={'tax_rate': profile.vat_percentage})
        formset = QuoteItemFormSet(prefix='items', queryset=QuoteItem.objects.none())

    inventory_items = InventoryItem.objects.filter(user=request.user)

    context = {
        'form': form,
        'formset': formset,
        'title': 'Create a New Quote',
        'inventory_items': inventory_items,
    }
    return render(request, 'invoices/quote_form.html', context)


@login_required
def quote_update(request, quote_id):
    """Handles updating an existing quote with line items."""
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote, user=request.user)
        formset = QuoteItemFormSet(request.POST, instance=quote, prefix='items')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('quote_detail', quote_id=quote.id)
    else:
        form = QuoteForm(instance=quote, user=request.user)
        formset = QuoteItemFormSet(instance=quote, prefix='items')

    inventory_items = InventoryItem.objects.filter(user=request.user)

    context = {
        'form': form,
        'formset': formset,
        'title': f'Edit Quote {quote.quote_number or f"#{quote.id}"}',
        'inventory_items': inventory_items,
    }
    return render(request, 'invoices/quote_form.html', context)


@login_required
def quote_delete(request, quote_id):
    """Handles deleting a quote after confirmation."""
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
    if request.method == 'POST':
        quote_str = str(quote)
        quote.delete()
        messages.success(request, f"Successfully deleted {quote_str}.")
        return redirect('quote_list')
    context = {'object': quote, 'form_type': 'Quote'}
    return render(request, 'invoices/generic_confirm_delete.html', context)


@login_required
def convert_quote_to_invoice(request, quote_id):
    """Converts an accepted quote into a new invoice."""
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
    if quote.is_converted():
        messages.info(request, f"Quote #{quote.id} has already been converted to Invoice #{quote.invoice.id}.")
        return redirect('quote_detail', quote_id=quote.id)
    if quote.status != 'accepted':
        messages.error(request,
                       f"Quote #{quote.id} cannot be converted because its status is '{quote.get_status_display()}', not 'Accepted'.")
        return redirect('quote_detail', quote_id=quote.id)

    if request.method == 'POST':
        with transaction.atomic():
            profile_locked = Profile.objects.select_for_update().get(user=request.user)

            new_invoice = Invoice.objects.create(
                user=request.user,
                customer=quote.customer,
                invoice_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=30),
                tax_rate=quote.tax_rate,
                # Also generate a number for the new invoice
                invoice_number=f"{profile_locked.invoice_prefix}{timezone.now().year}/{profile_locked.invoice_next_number:06d}"
            )

            profile_locked.invoice_next_number += 1
            profile_locked.save()

            invoice_items = [
                InvoiceItem(
                    invoice=new_invoice,
                    description=item.description,
                    long_description=item.long_description,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                ) for item in quote.items.all()
            ]
            InvoiceItem.objects.bulk_create(invoice_items)
            quote.invoice = new_invoice
            quote.save()
            return redirect('invoice_detail', invoice_id=new_invoice.id)

    context = {'quote': quote, 'title': f"Confirm Conversion of Quote #{quote.id}"}
    return render(request, 'invoices/confirm_quote_conversion.html', context)


@login_required
def customer_list(request):
    """Displays a list of all customers."""
    customers = Customer.objects.filter(user=request.user)
    return render(request, 'invoices/customer_list.html', {'customers': customers})


@login_required
@check_subscription_limit('customer')
def customer_create(request):
    """Handles creation of a new customer."""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            messages.success(request, f"Customer '{customer.name}' was created successfully.")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    context = {'form': form, 'form_type': 'Customer', 'title': 'Create a New Customer'}
    return render(request, 'invoices/generic_form.html', context)


@login_required
def customer_update(request, customer_id):
    """Handles editing an existing customer."""
    customer = get_object_or_404(Customer, pk=customer_id, user=request.user)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.name}' was updated successfully.")
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    context = {'form': form, 'form_type': 'Customer', 'title': f'Edit {customer.name}'}
    return render(request, 'invoices/generic_form.html', context)


@login_required
def customer_delete(request, customer_id):
    """Handles deleting a customer after confirmation."""
    customer = get_object_or_404(Customer, pk=customer_id, user=request.user)
    if request.method == 'POST':
        customer_str = str(customer)
        customer.delete()
        messages.success(request, f"Successfully deleted {customer_str}.")
        return redirect('customer_list')
    context = {'object': customer, 'form_type': 'Customer'}
    return render(request, 'invoices/generic_confirm_delete.html', context)


# --- List and Detail Views ---

@login_required
def invoice_list(request):
    """Displays a list of all invoices."""
    invoices = Invoice.objects.filter(user=request.user).select_related('customer')
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


@login_required
def quote_list(request):
    """Displays a list of all quotes."""
    quotes = Quote.objects.filter(user=request.user).select_related('customer')
    return render(request, 'invoices/quote_list.html', {'quotes': quotes})


@login_required
def invoice_detail(request, invoice_id):
    """Displays the details for a single invoice."""
    invoice = get_object_or_404(Invoice, pk=invoice_id, user=request.user)
    public_pdf_path = reverse('invoice_public_pdf', args=[invoice.uuid])
    full_public_url = request.build_absolute_uri(public_pdf_path)
    context = {
        'invoice': invoice,
        'public_share_url': full_public_url,
    }
    return render(request, 'invoices/invoice_detail.html', context)


@login_required
def quote_detail(request, quote_id):
    """Displays the details for a single quote."""
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)

    # Generate the full public URL for sharing
    public_share_path = reverse('public_quote_detail', args=[quote.uuid])
    public_share_url = request.build_absolute_uri(public_share_path)

    context = {
        'quote': quote,
        'public_share_url': public_share_url,  # Pass URL to template
    }
    return render(request, 'invoices/quote_detail.html', context)


# --- PDF Generation ---

def _render_to_pdf(request, template_path, context, filename):
    """Helper function to render a template to a PDF response."""
    html_string = render_to_string(template_path, context)
    try:
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf_file = html.write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return HttpResponse("An error occurred while generating the PDF.", status=500)


@login_required
def invoice_pdf(request, invoice_id):
    """Generates and serves a PDF for a specific invoice for the logged-in user."""
    invoice = get_object_or_404(Invoice, pk=invoice_id, user=request.user)
    context = {'invoice': invoice, 'profile': request.user.profile, 'user': request.user}
    safe_invoice_number = (invoice.invoice_number or f'invoice-{invoice.id}').replace('/', '-')
    filename = f'{safe_invoice_number}.pdf'

    return _render_to_pdf(request, 'invoices/invoice_pdf.html', context, filename)


@login_required
def quote_pdf(request, quote_id):
    """Generates and serves a PDF for a specific quote for the logged-in user."""
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
    context = {'quote': quote, 'profile': request.user.profile, 'user': request.user}
    safe_quote_number = (quote.quote_number or f'quote-{quote.id}').replace('/', '-')
    filename = f'{safe_quote_number}.pdf'
    return _render_to_pdf(request, 'invoices/quote_pdf.html', context, filename)


def invoice_public_pdf(request, invoice_uuid):
    """
    Generates and serves a PDF for a specific invoice using its public UUID.
    This view is NOT login-protected, allowing customers to access it.
    """
    invoice = get_object_or_404(Invoice, uuid=invoice_uuid)
    context = {
        'invoice': invoice,
        'profile': invoice.user.profile,
        'user': invoice.user
    }
    safe_invoice_number = (invoice.invoice_number or f'invoice-{invoice.id}').replace('/', '-')
    filename = f'{safe_invoice_number}.pdf'
    return _render_to_pdf(request, 'invoices/invoice_pdf.html', context, filename)


# --- Public Quote Acceptance Views ---

def public_quote_detail(request, quote_uuid):
    """
    Displays a public, non-authenticated view of a quote for customer acceptance.
    """
    quote = get_object_or_404(Quote, uuid=quote_uuid)
    context = {
        'quote': quote,
        'profile': quote.user.profile,
        'user': quote.user,
        'title': f"Quote {quote.quote_number or quote.id}"
    }
    return render(request, 'invoices/public_quote_detail.html', context)


def public_quote_respond(request, quote_uuid):
    """
    Handles the customer's response (Accept/Decline) from the public quote page.
    """
    quote = get_object_or_404(Quote, uuid=quote_uuid)
    if request.method == 'POST':
        response = request.POST.get('response')
        if quote.status in ['accepted', 'rejected']:
            messages.info(request, "A response has already been recorded for this quote.")
        elif response == 'accept':
            quote.status = 'accepted'
            quote.save()
            messages.success(request, "Thank you! The quote has been accepted.")
            # Optional: Send an email notification to the business owner here
        elif response == 'decline':
            quote.status = 'rejected'
            quote.save()
            messages.warning(request, "The quote has been declined.")
            # Optional: Send an email notification to the business owner here
        else:
            messages.error(request, "Invalid response.")

    return redirect('public_quote_detail', quote_uuid=quote.uuid)


# --- Inventory Views ---

@login_required
def inventory_list(request):
    """Displays a list of all of the user's inventory items."""
    inventory_items = InventoryItem.objects.filter(user=request.user)
    context = {
        'inventory_items': inventory_items,
        'title': 'My Inventory'
    }
    return render(request, 'invoices/inventory_list.html', context)


@login_required
def inventory_create(request):
    """Handles the creation of a new inventory item."""
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f"Item '{item.name}' was created successfully.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm()
    context = {
        'form': form,
        'title': 'Create New Item'
    }
    return render(request, 'invoices/inventory_form.html', context)


@login_required
def inventory_update(request, item_id):
    """Handles editing an existing inventory item."""
    item = get_object_or_404(InventoryItem, pk=item_id, user=request.user)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Item '{item.name}' was updated successfully.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    context = {
        'form': form,
        'title': f'Edit {item.name}'
    }
    return render(request, 'invoices/inventory_form.html', context)


@login_required
def inventory_delete(request, item_id):
    """Handles deleting an inventory item after confirmation."""
    item = get_object_or_404(InventoryItem, pk=item_id, user=request.user)
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f"Successfully deleted item '{item_name}'.")
        return redirect('inventory_list')
    context = {
        'object': item,
        'form_type': 'Inventory Item',
        'cancel_url': 'inventory_list'
    }
    return render(request, 'invoices/generic_confirm_delete.html', context)