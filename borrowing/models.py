from django.db import models
from rest_framework.generics import get_object_or_404

from book.models import Book
from library_service import settings
from user.models import User

from borrowing.management.commands.send_notification import notification


class Borrowing(models.Model):

    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    @staticmethod
    def validate_inventory(book, error_to_raise):
        print("BOOK_INVENTORYYYYYYYYYYYYYYYYYYYYYYYYYYY", book.inventory)
        if book.inventory < 1:
            raise error_to_raise("There are no books in inventory to borrow.")

    @staticmethod
    def validate_pending_payment(user, error_to_raise):
        pending_borrowings = user.borrowings.filter(payments__status="PN")
        print("PENDING_BORROWINGS", pending_borrowings)

        if pending_borrowings:
            raise error_to_raise("You have not yet completed your paying. "
                                 "Please complete it before borrowing a new book.")

    def save(self, *args, **kwargs):
        print("SAVE CALLED")
        book = get_object_or_404(Book, pk=self.book_id)
        message = (
            f"You have borrowed a book:\n'{book.title}'."
            f"\nExpected return date:"
            f"\n{self.expected_return_date}\n"
            f"Price:\n"
            f"{book.daily_fee} $"
        )
        if self.pk is None:
            notification(message)
            print("NOTIFICATION CALLED")
        super().save(*args, **kwargs)
