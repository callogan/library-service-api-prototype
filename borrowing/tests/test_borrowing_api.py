from datetime import datetime, timedelta
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
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer
)

BORROWING_URL = reverse("borrowing:borrowing-list")


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
    print("BORROWINGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", kwargs)
    print("BORROWINGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", borrowing)
    session_url = kwargs.get("session_url")
    print("BORROWINGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", session_url)
    session_id = kwargs.get("session_id")
    print("BORROWINGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", session_id)
    money_to_pay = kwargs.get("money_to_pay")

    defaults = {
        "status": "PN",
        "type": "P",
        "borrowing": borrowing,
        "session_url": session_url,
        "session_id": session_id,
        "money_to_pay": money_to_pay
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


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id):
    return reverse("borrowing:return-borrowing", args=[borrowing_id])


class UnauthenticatedPaymentApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
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
            inventory=2,
            daily_fee=10.0,
        )
        self.book_2 = Book.objects.create(
            title="Sample book 2",
            author="Test Author",
            cover="S",
            inventory=5,
            daily_fee=10.0,
        )
        self.book_3 = Book.objects.create(
            title="Sample book 3",
            author="Test Author",
            cover="S",
            inventory=4,
            daily_fee=10.0,
        )
        self.book_4 = Book.objects.create(
            title="Sample book 4",
            author="Test Author",
            cover="S",
            inventory=3,
            daily_fee=10.0,
        )
        print("SET_VALUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", self.user)

        self.borrowing_1 = Borrowing.objects.create(
            expected_return_date=datetime(2023, 9, 29).date(),
            book=self.book_1,
            user=self.user
        )

        self.borrowing_2 = Borrowing.objects.create(
            expected_return_date=datetime(2023, 9, 28).date(),
            book=self.book_2,
            user=self.user2
        )
        self.borrowing_3 = Borrowing.objects.create(
            expected_return_date=datetime(2023, 9, 30).date(),
            book=self.book_3,
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

    def test_list_borrowings(self):
        res = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        print("BORROWING_RESP_DATA", res.data)
        print("BORROWING_SERIALIZER_DATA", serializer.data)
        self.assertEqual(res.data[0], serializer.data[0])

    def test_retrieve_own_borrowing_detail(self):
        borrowing_user = self.borrowing_1
        borrowing_user2 = self.borrowing_2

        borrowing_user_url = detail_url(borrowing_user.id)
        borrowing_user2_url = detail_url(borrowing_user2.id)

        response1 = self.client.get(borrowing_user_url)
        response2 = self.client.get(borrowing_user2_url)

        serializer = BorrowingDetailSerializer(borrowing_user)

        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        self.assertEquals(response1.data, serializer.data)
        self.assertEquals(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_borrowing_create(self):
        print("СМОТРИ_ИДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДД", self.book_1.id)
        payload = {
            "expected_return_date": datetime(2024, 9, 28).date(),
            "book": self.book_1.id,
            "user": self.user.id,
        }

        print("INVENTORY", self.book_1.inventory)

        response = self.client.post(BORROWING_URL, payload)
        print("RESPONSE_DATA********************************************", response.data)
        self.book_1.change_amount_of_inventory()
        # print("BOOK_INVENTORY********************************************", book_inventory_after_borrowing)

        self.book_1.refresh_from_db()

        print("INVENTORY_AFTERRRRRRRRRRRRRRRRRR", self.book_1.inventory)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(self.book_1.inventory, 1)

    def test_borrowing_create_not_allowed_if_previous_not_payed(self):
        Payment.objects.create(
            status="PN",
            type="P",
            borrowing=self.borrowing_1,
            session_url="http:/example_1.com",
            session_id="fjnvdkjfnvkve",
            money_to_pay=10.0,
        )

        book = self.book_1
        payload = {
            "expected_return_date": datetime(2024, 9, 30).date(),
            "book": book.id,
            "user": self.user.id
        }

        response = self.client.post(BORROWING_URL, payload)
        print("RESPONSE_DATA_222********************************************", response.data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(
            response.data["non_field_errors"][0],
            "You have not yet completed your paying. Please complete it before borrowing a new book.",
        )

    def test_borrowing_create_not_allowed_if_zero_inventory(self):
        book = self.book_1
        self.borrowing_1 = Borrowing.objects.create(
            expected_return_date=datetime(2023, 9, 29).date(),
            book=book,
            user=self.user
        )

        book.change_amount_of_inventory()

        self.borrowing_2 = Borrowing.objects.create(
            expected_return_date=datetime(2023, 9, 30).date(),
            book=book,
            user=self.user2
        )

        book.change_amount_of_inventory()

        payload = {
            "expected_return_date": datetime(2024, 9, 25).date(),
            "book": book.id,
            "user": self.user3.id
        }

        response = self.client.post(BORROWING_URL, payload)
        print("RESPONSE_DATA_222********************************************", response.data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(
            response.data["non_field_errors"][0],
            "There are no books in inventory to borrow.",
        )

    def test_borrowing_return(self):
        borrowing = self.borrowing_1

        url = detail_url(borrowing.id) + "return-borrowing/"

        response = self.client.patch(url)
        response2 = self.client.patch(url)

        print(borrowing.__dict__)

        print("PAYMENTS", borrowing.payments.all())

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data["status"], "borrowing returned")
        self.assertEquals(
            response2.data["non_field_errors"][0],
            "Borrowing has been already returned.",
        )

    def test_create_payment(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=datetime(2024, 6, 1).date(),
            book=self.book_1,
            user=self.user
        )

        url = detail_url(borrowing.id) + "return-borrowing/"

        self.client.patch(url)

        borrowing.actual_return_date = datetime.now().date()

        print(borrowing.__dict__)
        print("ACTUAL_RETURN_DATE***********************************", borrowing.actual_return_date)
        print("EXPECTED_RETURN_DATE***********************************", borrowing.expected_return_date)
        borrowing_period = (borrowing.expected_return_date - borrowing.borrow_date).days
        overdue_period = (borrowing.actual_return_date - borrowing.expected_return_date).days
        borrowing_amount = int(self.book_1.daily_fee * borrowing_period * 100)
        overdue_amount = int(self.book_1.daily_fee * overdue_period * 100) * 2
        calculated_total_amount = borrowing_amount + overdue_amount

        payments = borrowing.payments.filter(status="PN", money_to_pay=80)
        self.assertTrue(payments.exists())
        self.assertEqual(payments.count(), 1)
        payment = payments.first()
        self.assertEqual(payment.money_to_pay, calculated_total_amount / 100)

    def test_filter_borrowings_is_active_true_or_false(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=datetime(2024, 9, 29).date(),
            book=self.book_1,
            user=self.user
        )
        borrowing2 = Borrowing.objects.create(
            expected_return_date=datetime(2024, 6, 12).date(),
            actual_return_date=datetime(2024, 9, 7).date(),
            book=self.book_2,
            user=self.user
        )
        borrowing3 = Borrowing.objects.create(
            expected_return_date=datetime(2024, 6, 13).date(),
            actual_return_date=datetime(2024, 9, 6).date(),
            book=self.book_3,
            user=self.user
        )
        borrowing4 = Borrowing.objects.create(
            expected_return_date=datetime(2024, 9, 30).date(),
            book=self.book_4,
            user=self.user
        )

        response1 = self.client.get(BORROWING_URL, payload={"is_active": "True"})
        response2 = self.client.get(BORROWING_URL, payload={"is_active": "False"})

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)
        serializer3 = BorrowingSerializer(borrowing3)
        serializer4 = BorrowingSerializer(borrowing4)

        print("RESPONSE_DATA_FIRSTTTTTTTTTTTTTTTT********************************************", response1.data)
        print("RESPONSE_DATA_SECONDDDDDDDDDDDDDDDD********************************************", response2.data)
        print("SERIALIZER_DATA_FIRST********************************************", serializer1.data)
        print("SERIALIZER_DATA_THIRD********************************************", serializer3.data)
        # self.assertIn(serializer1.data, response1.data)
        self.assertIn(serializer4.data, response1.data)
        self.assertIn(serializer3.data, response2.data)
        self.assertIn(serializer2.data, response2.data)

class AdminBorrowingApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.user2 = get_user_model().objects.create_user(
            "testunique1@tests.com", "unique_password"
        )
        self.user3 = get_user_model().objects.create_user(
            "testunique3@tests.com", "unique_password"
        )
        self.book = sample_book()
        self.client.force_authenticate(self.user)

    def test_list_all_borrowings(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=10),
            book=self.book,
            user=self.user2
        )
        borrowing2 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=10),
            book=self.book,
            user=self.user3
        )

        response = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()

        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data["results"], serializer.data)

    def test_borrowing_detail_another_user(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=datetime(2024, 9, 30).date(),
            book=self.book,
            user=self.user3
        )

        url = detail_url(borrowing.id)

        response = self.client.get(url)
        print("RESPONSE_DATA_!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", response.data)

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, serializer.data)

    def test_filter_borrowing_by_user_id(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=9),
            book=self.book,
            user=self.user2
        )
        borrowing2 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=10),
            book=self.book,
            user=self.user3
        )
        user = self.user3

        response = self.client.get(BORROWING_URL, data={"user": f"{user.id}"})

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, response.data["results"])
        self.assertNotIn(serializer1.data, response.data["results"])

    def test_filter_borrowings_is_active_true_or_false(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=9),
            book=self.book,
            user=self.user2,
        )
        borrowing2 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=10),
            actual_return_date=datetime.now().date() + timedelta(days=7),
            book=self.book,
            user=self.user2,
        )
        borrowing3 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=10),
            actual_return_date=datetime.now().date() + timedelta(days=8),
            book=self.book,
            user=self.user3
        )
        borrowing4 = Borrowing.objects.create(
            expected_return_date=datetime.now().date() + timedelta(days=9),
            book=self.book,
            user=self.user3,
        )

        response1 = self.client.get(BORROWING_URL, data={"is_active": "True"})
        response2 = self.client.get(BORROWING_URL, data={"is_active": "False"})

        print("ПОГАШЕНЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫ", response1.data)
        print("НЕПОГАШЕНЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫ", response2.data)

        borrowings_active_true = Borrowing.objects.filter(
            actual_return_date__isnull=True
        )
        borrowings_active_false = Borrowing.objects.filter(
            actual_return_date__isnull=False
        )

        serializer_active_true_borrowings = BorrowingSerializer(
            borrowings_active_true, many=True
        )
        serializer_active_false_borrowings = BorrowingSerializer(
            borrowings_active_false, many=True
        )

        print("SERIALIZER_22222222222222222222222222222222222", serializer_active_false_borrowings.data)

        self.assertEquals(
            response1.data["results"], serializer_active_true_borrowings.data
        )
        self.assertEquals(
            response2.data["results"], serializer_active_false_borrowings.data
        )
