from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICE = [("PN", "PENDING"), ("PD", "PAID"), ("EX", "Expired")]
    TYPE_CHOICE = [("P", "PAYMENT"), ("F", "FINE")]

    status = models.CharField(max_length=2, choices=STATUS_CHOICE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICE)
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_url = models.TextField(null=True, blank=True, unique=True)
    session_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    money_to_pay = models.DecimalField(max_digits=50, decimal_places=2)
    expires_at = models.DateTimeField(null=True, blank=True)
