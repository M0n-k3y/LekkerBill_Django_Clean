# F:/Python Apps/LekkerBill_Django_Clean/invoices/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
# You will need to import your own views for the dashboard, etc.
from . import views
from payfast import views as payfast_views # Import views from your custom payfast app

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

    # Main application sections
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/new/', views.invoice_create, name='invoice_create'), # Used in invoice_list.html
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/public-pdf/<uuid:public_id>/', views.invoice_public_pdf, name='invoice_public_pdf'),

    path('quotes/', views.quote_list, name='quote_list'), # Used in base.html
    path('quotes/new/', views.quote_create, name='quote_create'), # Used in quote_list.html
    path('quotes/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quotes/<int:pk>/pdf/', views.quote_pdf, name='quote_pdf'),
    path('quotes/<int:pk>/update/', views.quote_update, name='quote_update'),
    path('quotes/<int:pk>/delete/', views.quote_delete, name='quote_delete'),

    # Public-facing quote URLs for customers
    path('quotes/view/<uuid:public_id>/', views.quote_public_view, name='quote_public_view'),
    path('quotes/action/<uuid:public_id>/', views.quote_customer_action, name='quote_customer_action'),
    path('quotes/<int:pk>/convert/', views.convert_quote_to_invoice, name='convert_quote_to_invoice'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'), # Used in base.html
    path('inventory/new/', views.inventory_create, name='inventory_create'), # Used in inventory_list.html
    path('inventory/<int:pk>/edit/', views.inventory_update, name='inventory_update'), # Used in inventory_list.html
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'), # Used in inventory_list.html

    # Settings & Subscription URLs
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_update, name='settings_update'), # Used in base.html
    path('subscription/', views.subscription_detail, name='subscription_detail'), # Used in base.html
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'), # Used in subscription_detail.html
    path('subscription/reactivate/', views.reactivate_subscription, name='reactivate_subscription'), # Used in subscription_detail.html
    path('subscription/upgrade/', views.upgrade_to_pro, name='upgrade_to_pro'), # Used in subscription_detail.html

    # PayFast Integration URLs
    path('payfast/notify/', payfast_views.notify_handler, name='payfast_notify'),
    path('payfast/return/', views.payfast_return, name='payfast_return'),
    path('payfast/cancel/', views.payfast_cancel, name='payfast_cancel'),

    # Notification URLs
    path('notifications/mark-as-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),

    # PWA URL
    path('serviceworker.js', views.service_worker, name='serviceworker'),
    path('install/', views.install_pwa, name='install_pwa'),
]