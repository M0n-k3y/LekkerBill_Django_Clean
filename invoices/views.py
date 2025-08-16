from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CustomerForm # ✅ Keep your form imports
from .models import Customer, Quote, Invoice, Subscription # ✅ Import the models we need
 
# You would import your models here to get real data

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
        'subscription': request.user.subscription
    }
    return render(request, 'invoices/dashboard.html', context)

@login_required
def placeholder_view(request, *args, **kwargs):
    """A placeholder view for features that are not yet implemented."""
    messages.info(request, "This feature is coming soon!")
    return redirect('dashboard')

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