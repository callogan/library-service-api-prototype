from celery import shared_task
from .check_expired_payments import check_expiration_payments


@shared_task
def check_stripe_expired_payments():
    check_expiration_payments()
