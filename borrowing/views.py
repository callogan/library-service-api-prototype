from datetime import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from payment.payment_session import create_stripe_session
from .notification import send_overdue_borrowing_notification
from .serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer, BorrowingReturnSerializer, BorrowingCreateSerializer
)
from .models import Borrowing

from borrowing.tasks import overdue_borrowing_notifications


class BorrowingViewSet(
    viewsets.ModelViewSet #UpdateModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet
):
    queryset = Borrowing.objects.all()
    # print("BORROWINGs", queryset)
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    # print("TASK", send_overdue_borrowing_notification())

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # overdue_borrowing_notifications.delay()
        return response

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        if self.action in ("list", "retrieve") and self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user_id=self.request.user.id)

        user = self.request.query_params.get("user")
        is_active = self.request.query_params.get("is_active")
        # if is_active:
        #     self.queryset = self.queryset.filter(
        #         actual_return_date__isnull=True
        #     )
        if is_active:
            queryset = queryset.filter(
                actual_return_date__isnull=True
            )
            print("ВЬЮХА_КВЕРИСЕТ_ТРУ", queryset)
            for item in queryset:
                print("Actual return date (is_active=True):", item.actual_return_date)
        else:
            queryset = queryset.filter(
                actual_return_date__isnull=False
            )
            print("ВЬЮХА_КВЕРИСЕТ_ФОЛС", queryset)
            for item in queryset:
                print("Actual return date (is_active=False):", item.actual_return_date)
        if self.request.user.is_staff:
            """Filtering for admin users"""
            if user:
                user_id = self._params_to_ints(user)
                self.queryset = queryset.filter(user_id__in=user_id)
        # if not self.request.user.is_staff:
        #     """Filtering for non-admin users"""
        #     if is_active:
        #         self.queryset = self.queryset.filter(
        #             actual_return_date__isnull=True
        #         )
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return self.serializer_class

    @transaction.atomic
    @action(
        methods=["PATCH"],
        detail=True,
        url_path="return-borrowing",
        serializer_class=BorrowingReturnSerializer,
    )
    def return_borrowing(self, request, pk=None):
        print("REQUEST_DATAAAAAAAAAAAAAAAAA", request.data)
        borrowing = self.get_object()
        borrowings = Borrowing.objects.all()
        print("BORROWINGs", borrowings)
        book = borrowing.book
        actual_return_date = datetime.now().date()

        serializer_update = BorrowingReturnSerializer(
            borrowing,
            context={"request": self.request},
            data={"actual_return_date": actual_return_date},
            partial=True,
        )
        serializer_update.is_valid(raise_exception=True)
        serializer_update.save()
        return Response({"status": "borrowing returned"})
