# from django.utils import timezone
import logging
from datetime import datetime, timedelta

from borrowing.management.commands.send_notification import notification
from payment.models import Payment

logger = logging.getLogger(__name__)


def check_expiration_payments():
    current_time = datetime.now()
    expired_payments = Payment.objects.filter(
        expires_at__lte=current_time, status="PN"
    )

    for payment in expired_payments:
        payment.status = "EX"
        payment.save()

        notification(f"Session and payment for borrowing {payment.borrowing} is expired")

        logger.info(f"Payment {payment.id} is expired")
