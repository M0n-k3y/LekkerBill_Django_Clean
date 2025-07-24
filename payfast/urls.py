from django.urls import path
from . import views

# This line is crucial. It tells Django the namespace for this app.
app_name = 'payfast'

urlpatterns = [
    # This URL pattern points to your notify_handler view and gives it a name
    path('notify/', views.notify_handler, name='payfast_notify_url'),
]