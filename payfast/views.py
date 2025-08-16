import hashlib
import logging
from decimal import Decimal
from urllib.parse import quote_plus

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from invoices.models import Subscription
from .models import PayFastITN

logger = logging.getLogger(__name__)


def _validate_itn_with_payfast(raw_post_body_str: str) -> bool:
    """
    Makes a server-to-server request back to PayFast to validate the ITN data.
    """
    validation_url = "https://sandbox.payfast.co.za/eng/query/validate"
    if not settings.PAYFAST_SANDBOX_MODE:
        validation_url = "https://www.payfast.co.za/eng/query/validate"

    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(validation_url, data=raw_post_body_str, headers=headers, timeout=5)
        response.raise_for_status()
        return response.text == 'VALID'
    except requests.RequestException as e:
        logger.error("PayFast ITN validation request failed: %s", e)
        return False


@csrf_exempt
@transaction.atomic
def notify_handler(request):
    """
    Handles the Instant Transaction Notification (ITN) from PayFast for recurring subscriptions.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Use the raw, untouched request body for signature validation.
    raw_post_body = request.body.decode('utf-8')
    post_data = request.POST

    # Log the incoming ITN data
    itn_log = PayFastITN.objects.create(
        raw_post_data=raw_post_body,
        payment_status=post_data.get('payment_status', ''),
        amount_gross=Decimal(post_data.get('amount_gross', '0.00')),
        m_payment_id=post_data.get('m_payment_id'),
        token=post_data.get('token') # Store the subscription token
    )
    logger.info("Received ITN request. ITN Log ID: %s", itn_log.id)

    # --- VALIDATION STEP 1: LOCAL SIGNATURE CHECK ---
    received_signature = post_data.get('signature')
    payload_items = [p for p in raw_post_body.split('&') if not p.startswith('signature=')]
    payload_string = '&'.join(payload_items)
    passphrase = settings.PAYFAST_PASSPHRASE
    if passphrase:
        payload_string += f"&passphrase={quote_plus(passphrase)}"

    generated_signature = hashlib.md5(payload_string.encode('utf-8')).hexdigest()

    if generated_signature != received_signature:
        logger.warning("ITN Validation FAILED: Signature mismatch for ITN Log ID: %s", itn_log.id)
        itn_log.result = "SIGNATURE_MISMATCH"
        itn_log.save()
        return HttpResponse("Signature mismatch", status=400)
    logger.info("ITN Signature validation PASSED.")

    # --- VALIDATION STEP 2: SERVER-TO-SERVER VALIDATION ---
    if not _validate_itn_with_payfast(raw_post_body):
        logger.warning("ITN Validation FAILED: PayFast server validation failed for ITN Log ID: %s", itn_log.id)
        itn_log.result = "SERVER_VALIDATION_FAILED"
        itn_log.save()
        return HttpResponse("ITN validation failed", status=400)
    logger.info("ITN server validation PASSED.")

    # --- BUSINESS LOGIC ---
    payment_status = itn_log.payment_status
    subscription_token = itn_log.token

    if payment_status == 'COMPLETE':
        # This handles both the FIRST payment and all SUBSEQUENT monthly renewals.
        subscription_id = itn_log.m_payment_id
        subscription = get_object_or_404(Subscription, pk=subscription_id)
        itn_log.profile = subscription.user.profile # Link the log to the profile

        # Check if this is the first payment for this subscription
        if not subscription.payfast_token:
            logger.info("First payment for subscription %s. Activating Pro plan.", subscription.id)
            subscription.plan = 'pro'
            subscription.status = 'active'
            subscription.payfast_token = subscription_token
            # Set the end date to one month from now
            subscription.subscription_end_date = timezone.now().date() + relativedelta(months=1)
            itn_log.result = "SUCCESS_ACTIVATED"
        else:
            # This is a renewal payment
            logger.info("Renewal payment for subscription %s. Extending end date.", subscription.id)
            # Ensure the end date is always extended from the current end date, or from today if it lapsed
            current_end_date = subscription.subscription_end_date or timezone.now().date()
            subscription.subscription_end_date = current_end_date + relativedelta(months=1)
            subscription.status = 'active' # Ensure it's active if it lapsed
            itn_log.result = "SUCCESS_RENEWED"

        subscription.save()
        itn_log.save()

    elif payment_status == 'CANCELLED':
        # This handles a cancellation event from PayFast.
        if not subscription_token:
            logger.warning("Received CANCELLED status without a token. Cannot process. ITN Log ID: %s", itn_log.id)
            itn_log.result = "ERROR_CANCELLED_NO_TOKEN"
            itn_log.save()
            return HttpResponse("OK")

        try:
            subscription = Subscription.objects.get(payfast_token=subscription_token)
            itn_log.profile = subscription.user.profile
            subscription.status = 'cancelled'
            subscription.save()
            logger.info("Subscription %s (Token: %s) has been marked as cancelled.", subscription.id, subscription_token)
            itn_log.result = "SUCCESS_CANCELLED"
            itn_log.save()
        except Subscription.DoesNotExist:
            logger.error("Received cancellation for an unknown token: %s", subscription_token)
            itn_log.result = "ERROR_UNKNOWN_TOKEN"
            itn_log.save()

    else:
        # Handle other statuses like FAILED, PENDING, etc.
        logger.info("Received non-actionable status '%s' for ITN Log ID: %s. Acknowledging.", payment_status, itn_log.id)
        itn_log.result = f"IGNORED_STATUS_{payment_status}"
        itn_log.save()

    return HttpResponse("OK")