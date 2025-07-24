from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include the payfast URLs with a namespace so reverse('payfast:...') works
    path('payfast/', include(('payfast.urls', 'payfast'), namespace='payfast')),

    # Include all of your app's URLs from the invoices/urls.py file
    path('', include('invoices.urls')),
]

# This is important for serving user-uploaded logos during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)