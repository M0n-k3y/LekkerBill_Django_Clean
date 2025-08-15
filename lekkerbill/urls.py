# E:/LekkerBill_Django_Clean/lekkerbill/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # This new line makes the login page the site's homepage
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='home'),

    path('admin/', admin.site.urls),

    # This includes all the URLs from your 'invoices' app (dashboard, etc.)
    path('', include('invoices.urls')),
]

# This is a good practice for serving user-uploaded media files during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
