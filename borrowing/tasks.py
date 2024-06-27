from celery import shared_task
from borrowing.management.commands.send_notification import notification
from borrowing.notification import send_overdue_borrowing_notification

# borrowing/tasks.py
import logging
logger = logging.getLogger(__name__)


# def make_message(instance_borrowing, instance_book):
#     return (
#         f"You have borrowed a book:\n'{instance_book.title}'."
#         f"\nExpected return date:"
#         f"\n{instance_borrowing.expected_return_date}\n"
#         f"Price:\n"
#         f"{instance_book.daily_fee} $"
#     )
#
#
@shared_task
def borrowing_creation_notifications(instance_borrowing, instance_book):
    message = make_message(instance_borrowing, instance_book)
    notification(message)


@shared_task
def overdue_borrowing_notifications():
    logger.info("Starting overdue borrowing notification task...")
    send_overdue_borrowing_notification()
