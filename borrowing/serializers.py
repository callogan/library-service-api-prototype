import time
from datetime import datetime

import stripe
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import borrowing
from book.models import Book
from payment.models import Payment
from payment.payment_session import create_stripe_session, create_payment
from .models import Borrowing
from book.serializers import BookSerializer

from borrowing.management.commands.send_notification import notification

FINE_MULTIPLIER = 2


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )

    # def create(self, validated_data):
    #     print("Serializer create method called")
    #     print("VALIDATED_DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", validated_data)
    #     borrowing = Borrowing.objects.create(**validated_data)
    #     print("VALIDATED_DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", validated_data)
    #     book_id = validated_data["book_id"]
    #     book = Book.objects.get(pk=book_id)
    #     book.inventory -= 1
    #     book.save()
    #
    #     create_stripe_session(
    #         borrowing, request=self.context["request"]
    #     )
    #     # Получите все сессии
    #     sessions = stripe.checkout.Session.list()
    #
    #     # Перебираем и выводим все сессии
    #     for session in sessions.auto_paging_iter():
    #         print("SESSIONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN", session)
    #     print("Inventory amount changed")
    #     # Проверка вызова метода save
    #     if borrowing.save():
    #         print("Borrowing object saved successfully")
    #
    #         # Проверка вызова notification
    #         if notification:
    #             print("Notification sent successfully")
    #         else:
    #             print("Error sending notification")
    #     else:
    #         print("Error saving borrowing object")
    #     return borrowing


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book", "user")

    def validate(self, attrs):
        print("SELF", self)
        print("SELF_2", self.context["request"])
        # raise ValidationError("Validation failed at the beginning of the method.")
        data = super().validate(attrs)
        print("ATTRS", attrs)
        user = self.context["request"].user
        Borrowing.validate_inventory(
            attrs["book"],
            ValidationError
        )
        Borrowing.validate_pending_payment(user, ValidationError)
        return data

    # def validate(self, attrs):
    #     print("Метод validate вызван")
    #     data = super().validate(attrs)
    #     user = self.context["request"].user
    #     pending_payments = Payment.objects.filter(borrowing__user=user).filter(
    #         status="PN"
    #     )
    #     if pending_payments:
    #         raise ValidationError(
    #             detail="You have one or more pending payments. You can't make borrowings until you pay for them."
    #         )
    #     return data

    @transaction.atomic()
    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        return borrowing

class BorrowingListSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateField(format="%Y-%m-%d")
    actual_return_date = serializers.DateField(format="%Y-%m-%d")
    expected_return_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )

    def create(self, validated_data):
        print("SELF", self)
        print("SELF_2", self.context["request"])
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            return ExampleModel.objects.create(**validated_data)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance

        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        return None


class BorrowingDetailSerializer(BorrowingListSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            # "payments",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )
        read_only_fields = ("id", "borrow_date", "expected_return_date")

    @transaction.atomic
    def validate(self, attrs):
        borrowing = self.instance
        if borrowing.actual_return_date is not None:
            raise ValidationError(detail="Borrowing has been already returned.")

        actual_return_date = datetime.now().date()
        expected_return_date = borrowing.expected_return_date
        if actual_return_date > expected_return_date:
            print("YOU NEED CREATE SESSION OBJECT FOR FINE TO CHARGE")
        return super().validate(attrs=attrs)

    @transaction.atomic
    def update(self, instance, validated_data):
        book = instance.book
        instance.actual_return_date = datetime.now().date()
        instance.save()
        book.inventory += 1
        # actual_return_date = datetime.now().date()
        # expected_return_date = instance.expected_return_date
        # overdue_days = (actual_return_date - expected_return_date).days
        # money_for_borrowing = 0
        # money_for_overdue = 0
        # if overdue_days > 0:
        #     money_for_overdue = int(book.daily_fee * overdue_days * 100) * FINE_MULTIPLIER
        #     print("OVERDUE_MONEYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY", money_for_overdue)
        # else:
        #     money_for_borrowing = int(book.daily_fee * overdue_days * 100)
        #     print("BORROWING_MONEYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY", money_for_borrowing)
        # money_to_pay = money_for_borrowing + money_for_overdue
        request = self.context.get("request")
        borrowing_ = self.instance
        create_payment(borrowing_, request)
        book.save()
        payment = borrowing_.payments.first()  # Assuming a reverse relation named `payment_set`
        if payment:
            print(f"Payment ID: {payment.id}")
            print(f"Payment session: {payment.status}")
            print(f"Payment amount: {payment.type}")
            print(f"Payment borrowing: {payment.money_to_pay}")
        else:
            print("No payment object found.")
        return instance


# # Получаем текущее время в Unix формате
# current_time = timezone.now()
# current_unix_time = int(time.mktime(current_time.timetuple()))
#
# # Получаем все сессии
# sessions = stripe.checkout.Session.list()
#
# for session in sessions:
#     print(
#         "HERE IS SESSIONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN",
#         "status -", session["status"],
#         "created at -", session["created"],
#         "expired at -", session["expires_at"],
#         "boolean", session["status"] == "expired"
#     )
#
# # print("DATA_SESSION-N-N-N-N-n-N-N-n-N-N-N-N", sessions['data'])
# # Фильтруем сессии по условиям
# # filtered_sessions = [
# #     session for session in sessions['data']
# #     if session['expires_at'] <= current_unix_time and session['status'] != "expired"
# # ]
#
# filtered_sessions_opened = [
#     session for session in sessions['data']
#     if session.get('status') != "expired"
# ]
#
# filtered_sessions_expired = [
#     session for session in sessions['data']
#     if session.get('status') == "expired"
# ]
#
# print("FILTERED_SESSION_OPENED_COUNT", len(filtered_sessions_opened))
# print("FILTERED_SESSION_EXPIRED_COUNT", len(filtered_sessions_expired))
#
# # Дальнейшая работа с отфильтрованными сессиями
# # for session in filtered_sessions:
# #     print("FILTERED_SESSION", session)
