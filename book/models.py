from django.db import models


class Book(models.Model):
    COVER_CHOICES = [("H", "HARD"), ("S", "SOFT")]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=1, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def change_amount_of_inventory(self, increase=False):
        if increase:
            self.inventory += 1
        else:
            self.inventory -= 1
        self.save()
