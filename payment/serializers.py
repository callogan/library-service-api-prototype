from rest_framework import serializers

from borrowing.models import Borrowing
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    # borrowing = serializers.PrimaryKeyRelatedField(
    #     queryset=Borrowing.objects.all()
    # )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )


class PaymentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "money_to_pay"
        )


class PaymentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "session_url",
            "session_id",
            "money_to_pay"
        )
