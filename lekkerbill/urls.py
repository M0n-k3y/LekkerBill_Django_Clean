# F:/Python Apps/LekkerBill_Django_Clean/lekkerbill/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # This redirects the root URL '/' to the '/login/' page. It's the best approach.
    path('', RedirectView.as_view(url='/login/', permanent=True), name='home'),

    path('admin/', admin.site.urls),

    # It's good practice to include the URLs for all installed apps.
    # The namespace allows you to use reverse('payfast:...') in your templates.
    path('payfast/', include(('payfast.urls', 'payfast'), namespace='payfast')),

    # This includes all the URLs from your 'invoices' app (dashboard, login, etc.)
    path('', include('invoices.urls')),
]

# This is a good practice for serving user-uploaded media files during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)