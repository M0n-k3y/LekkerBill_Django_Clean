# F:/Python Apps/LekkerBill_Django_Clean/invoices/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
# You will need to import your own views for the dashboard, etc.
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # --- Authentication URLs ---
    # This is the URL that was causing the 404 error.
    # It tells Django to use its built-in LoginView and your login.html template.
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # The logout URL. When a user logs out, they will be redirected to the login page.
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # The signup URL, referenced in your login template.
    # You will need to create a `signup` view in invoices/views.py for this to work.
    path('signup/', views.signup, name='signup'),

    # The password reset URLs, referenced in your login template.
    # Django provides these views for you. You just need to create the corresponding templates.
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),


    # --- Add your other application URLs below this line ---
    # The following URLs are required by your templates to avoid `NoReverseMatch` errors.
    # They currently point to a placeholder view. You will replace `views.placeholder_view`
    # with your actual views as you build out each feature.

    # Main application sections
    path('invoices/', views.placeholder_view, name='invoice_list'), # Used in base.html
    path('invoices/new/', views.placeholder_view, name='invoice_create'), # Used in invoice_list.html
    # The following URLs are required by admin.py to prevent startup errors
    path('invoices/<int:pk>/', views.placeholder_view, name='invoice_detail'),
    path('invoices/<int:pk>/pdf/', views.placeholder_view, name='invoice_pdf'),
    path('invoices/<int:pk>/update/', views.placeholder_view, name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.placeholder_view, name='invoice_delete'),

    path('quotes/', views.placeholder_view, name='quote_list'), # Used in base.html
    path('quotes/new/', views.placeholder_view, name='quote_create'), # Used in quote_list.html

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # The following URLs are required by admin.py and templates
    path('quotes/<int:pk>/', views.placeholder_view, name='quote_detail'),
    path('quotes/<int:pk>/pdf/', views.placeholder_view, name='quote_pdf'),
    path('quotes/<int:pk>/update/', views.placeholder_view, name='quote_update'),
    path('quotes/<int:pk>/delete/', views.placeholder_view, name='quote_delete'),
    path('quotes/<int:pk>/convert/', views.placeholder_view, name='convert_quote_to_invoice'),

    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'), # Used in base.html
    path('inventory/new/', views.placeholder_view, name='inventory_create'), # Used in inventory_list.html
    path('inventory/<int:pk>/edit/', views.placeholder_view, name='inventory_update'), # Used in inventory_list.html
    path('inventory/<int:pk>/delete/', views.placeholder_view, name='inventory_delete'), # Used in inventory_list.html

    # Settings & Subscription URLs
    path('settings/', views.placeholder_view, name='settings_update'), # Used in base.html
    path('subscription/', views.placeholder_view, name='subscription_detail'), # Used in base.html
    path('subscription/cancel/', views.placeholder_view, name='cancel_subscription'), # Used in subscription_detail.html
    path('subscription/reactivate/', views.placeholder_view, name='reactivate_subscription'), # Used in subscription_detail.html
    path('subscription/upgrade/', views.placeholder_view, name='upgrade_to_pro'), # Used in subscription_detail.html
]