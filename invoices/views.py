from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
 
# You would import your models here to get real data
# from .models import Customer, Quote, Invoice, Subscription

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
    # This is placeholder data. You should replace this with real queries
    # to your models once they are created.
    context = {
        'customer_count': 0, # Customer.objects.filter(user=request.user).count()
        'quote_count': 0,    # Quote.objects.filter(user=request.user).count()
        'invoice_count': 0,  # Invoice.objects.filter(user=request.user).count()
        'recent_invoices': [], # Invoice.objects.filter(user=request.user).order_by('-invoice_date')[:5]
        'recent_quotes': [],   # Quote.objects.filter(user=request.user).order_by('-created_at')[:5]
        'subscription': {      # A placeholder subscription object
            'plan': 'free',
            'is_currently_active': False
        }
    }
    return render(request, 'invoices/dashboard.html', context)

@login_required
def placeholder_view(request, *args, **kwargs):
    """A placeholder view for features that are not yet implemented."""
    messages.info(request, "This feature is coming soon!")
    return redirect('dashboard')