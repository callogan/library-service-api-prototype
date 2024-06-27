import stripe

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import mixins, status, generics, viewsets

from borrowing.models import Borrowing
from payment.models import Payment
from payment.payment_session import create_stripe_session, send_payment_notification
from payment.serializers import PaymentSerializer, PaymentListSerializer, PaymentDetailSerializer


class PaymentViewSet(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    generics.CreateAPIView,
    viewsets.GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    # payment = Payment.objects.get(pk=77)
    # print("PAYMENT_STATUS", payment.status)
    # print("PAYMENT_expiration", payment.expires_at)
    # print("PAYMENT_SESSION_ID", payment.session_id)

    # payments = Payment.objects.all()
    # for payment in payments:
    #     print(payment.__dict__)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            print("USER_STAFFFFFFFFFFFFFFFFFFFFFF", self.request.user)
            return super().get_queryset()
        print("USER_HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", self.request.user)
        return super().get_queryset().filter(borrowing__user=self.request.user)

    @action(
        methods=["GET"],
        detail=False,
        url_path="payment_success",
        url_name="success",
        permission_classes=[AllowAny]
    )
    def payment_success(self, request: Request):
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        print("SESSION_IDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", session_id)
        # Получаем все сессии
        sessions = stripe.checkout.Session.list()
        print("SESSIONSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS-ss-s-s-s", sessions["data"][0])

        for session in sessions:
            print(
                "HERE IS SESSIONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN222222222222222222222222222222222222222",
                "session_id -", session["id"],
            )
        session = stripe.checkout.Session.retrieve(session_id)
        print("************************************************************", session.payment_status)
        if session.payment_status == "paid":
            "ROFLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
            serializer = PaymentDetailSerializer(
                payment, data={"status": "PD"}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            send_payment_notification(payment)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"],
        detail=False,
        url_path="payment_cancel",
        url_name="cancel",
    )
    def payment_cancel(self, request: Request):
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        serializer = PaymentSerializer(payment)
        data = {
            "message": "You can make a payment during the next 2 hours.",
            **serializer.data,
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="update_session_url",
    )
    def recreate_expired_borrowing_session_url(self, request, pk=None):
        print("PAYMENT-T-T-T-T-T-T-T-T-T-T-T-T-T-T-T*************************************")
        payments = Payment.objects.all()
        print("PAYMENT-T-T-T-T-T-T-T-T-T-T-T-T-T-T-T-S-S-S", payments)
        print("PKKKKKKKKKKKKKKKKKKKKKKKKK", pk)
        # payment = payments.first()
        payment = self.get_object()
        print("PAYMENT-T-T-T-T-T-T-T-T-T-T-T-T-T-T-T", payment.id)
        # payment = Payment.objects.get(borrowing=borrowing, type="Payment")
        borrowing = payment.borrowing
        print("BORROWING-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G-G", payment.__dict__)
        if payment.status == "EX":
            print("I AM HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            new_session_for_borrowing = create_stripe_session(
                borrowing=borrowing, request=self.request
            )
            payment.status = "PN"
            payment.session_id = new_session_for_borrowing.id
            print("PAYMENT_IDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", payment.session_id)
            print("PAYMENT_URLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",payment.session_url)
            payment.session_url = new_session_for_borrowing.url
            payment.save()
            return Response({"status": "Session url has been updated"})

        return Response({"status": "Session url is still active"})
