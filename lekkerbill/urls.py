from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The standard path for the Django admin interface.
    path('admin/', admin.site.urls),

    # This is the crucial line. It tells Django to send all other requests
    # to your 'invoices' app's urls.py file to be handled. This will
    # resolve the 404 error on your homepage.
    path('', include('invoices.urls')),
]

# This is a standard helper pattern for serving user-uploaded media files
# (like company logos) during local development (when DEBUG=True).
# This part is ignored in production, as DigitalOcean serves these files differently.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)