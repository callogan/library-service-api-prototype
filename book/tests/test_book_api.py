from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import stripe
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework import status, request

from book.models import Book
from book.serializers import BookListSerializer, BookSerializer
from borrowing.models import Borrowing
from payment.models import Payment
from payment.payment_session import create_stripe_session
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer
)

BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    defaults = {
        "title": "test_title",
        "author": "test_author",
        "cover": "S",
        "inventory": 20,
        "daily_fee": 20.0,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


class UnauthenticatedBooksApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.book = sample_book()

    def test_list_books_auth_not_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_create_book_not_allowed(self):
        payload = {
            "title": "test_title",
            "author": "test_author",
            "cover": "S",
            "inventory": 25,
            "daily_fee": 25.0,
        }
        response = self.client.post(BOOK_URL, payload)

        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_book_allowed(self):
        book = sample_book()
        url = detail_url(book.id)

        response = self.client.get(url)

        self.assertEquals(response.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testunique@tests.com", "unique_password"
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_list_books(self):
        response = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        print("RESPONSE_DATA", response.data)
        self.assertEquals(response.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = self.book

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_book_create_book_not_allowed(self):
        payload = {
            "title": "test_title",
            "author": "test_author",
            "cover": "S",
            "inventory": 25,
            "daily_fee": 25.0,
        }
        response = self.client.post(BOOK_URL, payload)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_update_not_allowed(self):
        book = self.book

        url = detail_url(book.id)

        payload = {
            "title": "test_title_update",
            "author": "test_author_update",
            "cover": "H",
            "inventory": 26,
            "daily_fee": 30.0,
        }

        res = self.client.put(url, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_delete_not_allowed(self):
        book = self.book

        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_book_create(self):
        payload = {
            "title": "test_title_create",
            "author": "test_author_create",
            "cover": "S",
            "inventory": 100,
            "daily_fee": 100.0,
        }

        res = self.client.post(BOOK_URL, payload)
        serializer = BookSerializer(res.data, many=False)

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        self.assertEquals(res.data, serializer.data)

    def test_book_update(self):
        book = self.book
        url = detail_url(book.id)

        payload = {
            "title": "test_title_create",
            "author": "test_author_create",
            "cover": "S",
            "inventory": 100,
            "daily_fee": 100.0,
        }

        res = self.client.put(url, payload)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_book_delete(self):
        book = self.book
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)