from django.db import models

from library_service.settings import AUTH_USER_MODEL


class TelegramUser(models.Model):
    user_id = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer"
    )
    chat_id = models.IntegerField(unique=True)

