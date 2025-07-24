from django.db import models
from invoices.models import Profile

class PayFastITN(models.Model):
    """
    Represents a single Instant Transaction Notification from PayFast.
    This is used for logging and debugging all incoming payment notifications.
    """
    # Link to the user's profile if possible
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)

    # Raw data from PayFast
    raw_post_data = models.TextField()
    payment_status = models.CharField(max_length=255, blank=True)
    amount_gross = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # ✅ ADD THESE TWO NEW FIELDS
    m_payment_id = models.CharField(max_length=255, blank=True, null=True, help_text="Merchant's internal payment ID (e.g., Subscription ID)")
    token = models.CharField(max_length=255, blank=True, null=True, help_text="PayFast's unique token for a recurring subscription")

    # Our internal result
    result = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ITN Log #{self.id} - Status: {self.payment_status}"

    class Meta:
        verbose_name = "PayFast ITN Log"
        verbose_name_plural = "PayFast ITN Logs"
        ordering = ['-created_at']