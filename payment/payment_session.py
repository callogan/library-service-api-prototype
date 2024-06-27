import time
from datetime import datetime, timedelta

import stripe
from django.conf import settings
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.reverse import reverse
from timezone_field.backends import pytz

from borrowing.management.commands.send_notification import notification
from borrowing.models import Borrowing
from payment.models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY
LATE_FEE_MULTIPLIER = 2


def calculate_rental_fee_amount(borrowing: Borrowing) -> int:
    """Calculates amount user has to pay for borrowing"""
    borrowing_days = (borrowing.expected_return_date
                      - borrowing.borrow_date).days
    book_price = borrowing.book.daily_fee
    return int(book_price * borrowing_days * 100)


def calculate_late_fee_amount(borrowing: Borrowing) -> int:
    """Calculates amount user has to pay for overdue expected return date"""
    overdue_days = (borrowing.actual_return_date
                    - borrowing.expected_return_date).days
    book_price = borrowing.book.daily_fee
    return int(book_price * LATE_FEE_MULTIPLIER * overdue_days * 100)


def create_payment(borrowing: Borrowing, request):
    try:
        # Принты перед созданием объекта Payment

        # adjusted_time = timezone.now() + timezone.timedelta(minutes=43) #  datetime.fromtimestamp(session.expires_at)
        payment = Payment.objects.create(
            status="PN",
            borrowing=borrowing
        )

        checkout_session = create_stripe_session(borrowing, request)

        payment.session_id = checkout_session.id
        payment.session_url = checkout_session.url
        payment.money_to_pay = checkout_session.amount_total
        adjusted_expiration_time = datetime.fromtimestamp(checkout_session.expires_at)
        payment.expires_at = adjusted_expiration_time

        payment.save()
        # Принты после успешного создания объекта
        print(f"Payment created successfully with ID: {payment.id}")
        return payment

    except Exception as e:
        # Принт при возникновении ошибки
        print(f"Error occurred while creating payment: {e}")
        raise


def create_stripe_session(borrowing: Borrowing, request: Request):
    book = borrowing.book
    if (
            borrowing.actual_return_date
            and borrowing.actual_return_date > borrowing.expected_return_date
    ):
        rental_fee_amount = calculate_rental_fee_amount(borrowing)
        late_fee_amount = calculate_late_fee_amount(borrowing)
        total_amount = rental_fee_amount + late_fee_amount
        product_name = f"Payment for borrowing of {book.title}, consisting of rental fee amount {rental_fee_amount} " \
                       f"and late fee amount {late_fee_amount}"
    else:
        total_amount = calculate_rental_fee_amount(borrowing)
        product_name = f"Payment for borrowing of {book.title}, including only rental fee amount {total_amount}"

    print(f"Total amount (in cents): {total_amount}")
    print(f"Product name: {product_name}")

    success_url = reverse("payments:payment-success", request=request)
    cancel_url = reverse("payments:payment-cancel", request=request)
    price_data = stripe.Price.create(
        unit_amount=total_amount,
        currency="usd",
        product_data={
            "name": product_name,
        },
    )

    print(f"Price data ID: {price_data.id}")

    time_ = int(time.mktime((timezone.now() + timezone.timedelta(minutes=43)).timetuple()))
    print("TIME", time_)
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": price_data.id,
                "quantity": 1,
            }
        ],
        mode="payment",
        # success_url="http://localhost:8000/success/",
        # cancel_url="http://localhost:8000/cancel/",
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url + "?session_id={CHECKOUT_SESSION_ID}",
        expires_at=int(time.mktime((datetime.now() + timedelta(minutes=31)).timetuple()))
    )
    print("SESSION_EXPIRATION", session.expires_at)
    return session


def send_payment_notification(payment):
    message = f"You have successfully paid {payment.money_to_pay}$\n" \
              f"Your borrowing ID: {payment.borrowing_id}"
    notification(message)
