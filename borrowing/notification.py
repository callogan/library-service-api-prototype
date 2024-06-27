import logging

from django.utils import timezone

from borrowing.management.commands.send_notification import notification

from .models import Borrowing

logger = logging.getLogger(__name__)


def get_overdue_borrowings():
    overdue = timezone.now()
    return Borrowing.objects.filter(expected_return_date__lte=overdue)


def send_overdue_borrowing_notification():
    borrowings = get_overdue_borrowings()
    if not borrowings:
        notification("There are no overdue book borrowings today")

    for borrowing in borrowings:
        logger.info(f"Creating message for book borrowing id: {borrowing.id}")
        message = f"The expiration date of your book borrowing is " \
                  f"{borrowing.expected_return_date}.\n" \
                  f"Please return the book '{borrowing.book.title}' " \
                  f"by that time."
        notification(message)
        logger.info(f"The message was successfully sent")
