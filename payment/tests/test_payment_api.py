import datetime
from unittest.mock import patch, MagicMock

import stripe
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework import status, request

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
from payment.payment_session import create_stripe_session
from payment.serializers import PaymentListSerializer, PaymentDetailSerializer, PaymentSerializer

PAYMENT_URL = reverse("payment:payment-list")
SUCCESS_URL = reverse("payments:payment-success")
CANCEL_URL = reverse("payments:payment-cancel")
# RECREATE_URL = reverse("payments:update-session-url")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Test Author",
        "cover": "S",
        "inventory": 5,
        "daily_fee": 10.0,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**kwargs):
    book = sample_book()
    user = kwargs.get("user")
    defaults = {
        "expected_return_date": datetime.date(2024, 10, 29),
        "book_id": book.id,
        "user": user
    }
    defaults.update(kwargs)

    return Borrowing.objects.create(**defaults)


def sample_payment(**kwargs):
    borrowing = kwargs.get("borrowing")
    session_url = kwargs.get("session_url")
    session_id = kwargs.get("session_id")
    money_to_pay = kwargs.get("money_to_pay")

    defaults = {

        "borrowing": borrowing,

    }
    defaults.update(kwargs)

    # print(f'Trying to save Payment with session_id: {payment.session_id}')
    return Payment.objects.create(**defaults)


# payment = sample_payment()
# print("Sample Payment ID:", payment.id)
# print("Sample Payment Borrowing ID:", payment.borrowing_id)
# print("Sample Payment Session ID:", payment.session_id)
# if payment.borrowing.user_id:
#     print("Sample Payment Borrowing User ID:", payment.borrowing.user_id)
# else:
#     print("Sample Payment Borrowing User ID is missing")


def detail_url(payment_id):
    return reverse("payment:payment-detail", args=[payment_id])


class UnauthenticatedPaymentApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PAYMENT_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass1",
        )
        self.user2 = get_user_model().objects.create_user(
            "test2@test.com",
            "testpass2",
        )
        self.user3 = get_user_model().objects.create_user(
            "test3@test.com",
            "testpass3",
        )
        print("USER_IDDDDDDDDDDDDDDDDDDDDDDDDDDDD", self.user.id)
        self.client.force_authenticate(self.user)
        # print("BORROWING_1111111111111111111111111111111111", self.user_auth_payment.borrowing.user_id)
        # book_2 = sample_book(title="Sample title 2")
        # book_3 = sample_book(title="Sample title 3")
        # user_2_borrowing = sample_borrowing(book_id=book_2.id, user_id=2)
        # user_3_borrowing = sample_borrowing(book_id=book_3.id, user_id=3)
        # print("BORROWING_22222222222222222222222222222", user_2_borrowing.user_id)
        # print("BORROWING_33333333333333333333333333333",  user_3_borrowing.user_id)
        # self.user_2_payment = sample_payment(borrowing=user_2_borrowing, session_url="http:/example_2.com", session_id="fjnvdkjfnvknb")
        # self.user_3_payment = sample_payment(borrowing=user_3_borrowing, session_url="http:/example_3.com", session_id="fjnvdkjfnvkbv")
        # print("USER_!!!!!", self.user_auth_payment)
        # print("USER_222222", self.user_2_payment)
        # print("USER_3333333333", self.user_3_payment)
        self.book_1 = Book.objects.create(
            title="Sample book 1",
            author="Test Author",
            cover="S",
            inventory=5,
            daily_fee=10.0,
        )
        self.book_2 = Book.objects.create(
            title="Sample book 2",
            author="Test Author",
            cover="S",
            inventory=6,
            daily_fee=10.0,
        )
        self.book_3 = Book.objects.create(
            title="Sample book",
            author="Test Author",
            cover="S",
            inventory=7,
            daily_fee=10.0,
        )
        print("SET_VALUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", self.user)

        self.borrowing_1 = Borrowing.objects.create(
            expected_return_date=datetime.date(2023, 9, 29),
            book_id=self.book_1.id,
            user=self.user
        )

        self.borrowing_2 = Borrowing.objects.create(
            expected_return_date=datetime.date(2023, 9, 28),
            book_id=self.book_2.id,
            user=self.user2
        )
        self.borrowing_3 = Borrowing.objects.create(
            expected_return_date=datetime.date(2023, 9, 30),
            book_id=self.book_3.id,
            user=self.user3
        )
        # price_data = stripe.Price.create(
        #     unit_amount=1200,
        #     currency="usd",
        #     product_data={
        #         "name": f"Payment for borrowing of {self.book_1.title}",
        #     },
        # )
        # self.session = stripe.checkout.Session.create(
        #     line_items=[
        #         {
        #             "price": price_data.id,
        #             "quantity": 1,
        #         }
        #     ],
        #     mode="payment",
        #     # success_url="http://localhost:8000/success/",
        #     # cancel_url="http://localhost:8000/cancel/",
        #     success_url=SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
        #     cancel_url=CANCEL_URL + "?session_id={CHECKOUT_SESSION_ID}"
        # )
        self.factory = RequestFactory()

    def test_list_payments(self):
        response = self.client.get(PAYMENT_URL)

        payments_only_auth_user = Payment.objects.filter(borrowing__user=self.user)
        print("PAYMENTS_ALL", Payment.objects.filter(borrowing__user=self.user))
        payments = Payment.objects.all()
        for payment in payments:
            print(f"Payment ID: {payment.id}, Borrowing ID: {payment.borrowing.id}, {payment.borrowing.user_id}")

        print("USERRRRRRRRRRRRRRRRRRRRRRRRRRRRRR", self.user.id)
        print("PAYMENTSSSSSSSSSSSSSSSSSSSSSSSSS", payments_only_auth_user)
        serializer = PaymentListSerializer(payments_only_auth_user, many=True)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        print("RESPONSE_DATA_INTEGERSSSSSSSSSSSSSSSSSSSSSSS", response.data)
        print("SERIALIZER_DATA_INTEGERSSSSSSSSSSSSSSSSSSSSSSS", serializer.data)
        self.assertEquals(response.data, serializer.data)

    def test_user_can_see_only_his_own_payments(self):
        # book_4 = sample_book(title="Sample title 4")
        # borrowing_2 = sample_borrowing(book_id=book_4.id, user_id=2)
        own_payment = sample_payment(
            borrowing=self.borrowing_1,
            session_url="http:/example_1.com",
            session_id="fjnvdkjfnvkve",
            money_to_pay=self.borrowing_1.book.daily_fee
        )
        print("PAYMENT", own_payment.__dict__)
        another_user_payment = sample_payment(
            borrowing=self.borrowing_2,
            session_url="http:/example_2.com",
            session_id="fjnvdkjfnvkdf",
            money_to_pay=self.borrowing_2.book.daily_fee
        )

        # Debugging: print all Payment objects
        all_payments = Payment.objects.all()
        for payment in all_payments:
            print(f'Payment ID: {payment.id}, session_id: {payment.session_id}, borrowing_id: {payment.borrowing_id}')

        # own_url_payment = detail_url(own_payment.id)
        own_url_payment = reverse('payment:payment-detail', args=[own_payment.id])
        print("URLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL", own_url_payment)
        another_user_url_payment = detail_url(another_user_payment.id)

        response_own = self.client.get(own_url_payment)
        response_another_user = self.client.get(another_user_url_payment)

        # Проверка аутентификации пользователя
        if '_auth_user_id' in self.client.session:
            user_id = self.client.session['_auth_user_id']
            print("User is authenticated with user ID:", user_id)
        else:
            print("User is not authenticated")

        serializer_own = PaymentDetailSerializer(own_payment)

        print("RESPONSE", response_own.content)
        # self.assertEquals(response_own.status_code, status.HTTP_200_OK)
        print("RESPONSE_DATA_OWNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN", response_own.data)
        print("SERIALIZER_DATA_OWNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN", serializer_own.data)
        self.assertEquals(response_own.data, serializer_own.data)
        self.assertEquals(response_another_user.status_code, status.HTTP_404_NOT_FOUND)

    @patch("payment.payment_session.send_payment_notification")
    @patch("stripe.checkout.Session.retrieve")
    def test_payment_success(self, mock_session_retrieve, mock_data):
        price_data = stripe.Price.create(
            unit_amount=1200,
            currency="usd",
            product_data={
                "name": f"Payment for borrowing of {self.book_1.title}",
            },
        )
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_data.id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/"
        )

        payment_user = sample_payment(
            borrowing=self.borrowing_1,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=self.borrowing_1.book.daily_fee
        )

        mock_session_retrieve.return_value = MagicMock(payment_status="paid")
        print("MOCK_TO_SEE", mock_data)
        url_success_payment = (
                SUCCESS_URL + f"?session_id={payment_user.session_id}"
        )

        response = self.client.get(url_success_payment)

        payment = Payment.objects.get(session_id=payment_user.session_id)
        print("STATUS********************************", payment.status)
        # print("PATCH", mock_data_2)

        serializer = PaymentDetailSerializer(payment)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, serializer.data)
        self.assertEquals(payment.status, "PD")

    def test_payment_cancel(self):
        price_data = stripe.Price.create(
            unit_amount=1200,
            currency="usd",
            product_data={
                "name": f"Payment for borrowing of {self.book_1.title}",
            },
        )
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_data.id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/"
        )

        payment_user = sample_payment(
            borrowing=self.borrowing_1,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=self.borrowing_1.book.daily_fee
        )
        url_cancel_payment = CANCEL_URL + f"?session_id={payment_user.session_id}"

        response = self.client.get(url_cancel_payment)
        serializer = PaymentSerializer(payment_user)

        self.assertEquals(
            response.data["message"], "You can make a payment during the next 2 hours."
        )
        self.assertEquals(response.data["id"], serializer.data["id"])
        self.assertEquals(response.data["status"], serializer.data["status"])
        self.assertEquals(response.data["type"], serializer.data["type"])
        self.assertEquals(response.data["borrowing"], serializer.data["borrowing"])
        self.assertEquals(response.data["session_url"], serializer.data["session_url"])
        self.assertEquals(response.data["session_id"], serializer.data["session_id"])
        self.assertEquals(
            response.data["money_to_pay"], serializer.data["money_to_pay"]
        )

    def test_recreate_expired_borrowing_session_url(self):
        borrowing = sample_borrowing(user=self.user)

        price_data = stripe.Price.create(
            unit_amount=1200,
            currency="usd",
            product_data={
                "name": f"Payment for borrowing of {self.book_1.title}",
            },
        )
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_data.id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/"
        )

        payment = sample_payment(
            borrowing=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=borrowing.book.daily_fee
        )

        payment.status = "EX"
        payment.save()

        url = reverse('payment:payment-recreate-expired-borrowing-session-url', args=[payment.id])

        request = self.factory.post(url)
        request.user = self.user

        response = self.client.post(url)

        payment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(payment.session_id, session.id)
        self.assertNotEqual(payment.session_url, session.url)
        self.assertEqual(payment.status, "PN")
        self.assertEqual(response.data['status'], "Session url has been updated")


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.user2 = get_user_model().objects.create_user(
            "test2@test.com",
            "testpass2",
        )
        self.user3 = get_user_model().objects.create_user(
            "test3@test.com",
            "testpass3",
        )
        self.client.force_authenticate(self.user)

    def test_admin_can_see_all_payments(self):
        borrowing_1 = sample_borrowing(user=self.user)
        borrowing_2 = sample_borrowing(user=self.user2)
        borrowing_3 = sample_borrowing(user=self.user3)

        payment_1 = sample_payment(borrowing=borrowing_1, money_to_pay=600)
        payment_2 = sample_payment(borrowing=borrowing_2, money_to_pay=800)
        payment_3 = sample_payment(borrowing=borrowing_3, money_to_pay=1200)

        res = self.client.get(PAYMENT_URL)

        serializer_1 = PaymentListSerializer(payment_1)
        serializer_2 = PaymentListSerializer(payment_2)
        serializer_3 = PaymentListSerializer(payment_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertIn(serializer_3.data, res.data)
