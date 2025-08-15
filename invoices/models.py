from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    """Represents a customer associated with a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name