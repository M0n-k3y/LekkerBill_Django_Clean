from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # --- Auth URLs ---
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('settings/', views.settings_update, name='settings_update'),

    # --- Password Reset URLs ---
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt'
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # --- Subscription URLs ---
    path('subscription/', views.subscription_detail, name='subscription_detail'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('subscription/reactivate/', views.reactivate_subscription, name='reactivate_subscription'),

    # --- Subscription Payment URLs ---
    path('subscription/upgrade/', views.upgrade_to_pro, name='upgrade_to_pro'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),

    # --- Invoice URLs ---
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/new/', views.invoice_create, name='invoice_create'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/edit/', views.invoice_update, name='invoice_update'),
    path('invoice/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoice/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoice/public/<uuid:invoice_uuid>/pdf/', views.invoice_public_pdf, name='invoice_public_pdf'),

    # --- Quote URLs ---
    path('quotes/', views.quote_list, name='quote_list'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('quote/new/', views.quote_create, name='quote_create'),
    path('quote/<int:quote_id>/edit/', views.quote_update, name='quote_update'),
    path('quote/<int:quote_id>/convert/', views.convert_quote_to_invoice, name='convert_quote_to_invoice'),
    path('quote/<int:quote_id>/delete/', views.quote_delete, name='quote_delete'),
    path('quote/<int:quote_id>/pdf/', views.quote_pdf, name='quote_pdf'),

    # ✅ ADDED: Public Quote Acceptance URLs
    path('quote/view/<uuid:quote_uuid>/', views.public_quote_detail, name='public_quote_detail'),
    path('quote/view/<uuid:quote_uuid>/respond/', views.public_quote_respond, name='public_quote_respond'),

    # --- Customer URLs ---
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/new/', views.customer_create, name='customer_create'),
    path('customer/<int:customer_id>/edit/', views.customer_update, name='customer_update'),
    path('customer/<int:customer_id>/delete/', views.customer_delete, name='customer_delete'),

    # --- Inventory URLs ---
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/new/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:item_id>/edit/', views.inventory_update, name='inventory_update'),
    path('inventory/<int:item_id>/delete/', views.inventory_delete, name='inventory_delete'),
]