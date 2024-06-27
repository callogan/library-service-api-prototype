from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from notification.models import TelegramUser


def is_user(message):
    user_email = message.text
    if get_user_model().objects.filter(email=user_email).exists():
        user = get_user_model().objects.get(email=user_email)
        try:
            TelegramUser.objects.get(user_id=user)
        except TelegramUser.DoesNotExist:
            TelegramUser.objects.create(user_id=user, chat_id=message.chat.id)
        return True
    return False


def welcome_message(bot, message) -> None:
    bot.reply_to(message,
                 f"Hello, {message.from_user.full_name}!\n"
                 f"Welcome to the Library Service!\n"
                 f"/help for more information")


def memo_items(bot, message) -> None:
    bot.reply_to(message,
                 "/start - start bot\n"
                 "/help - show information about commands\n"
                 "/my_borrowings - show all your borrowings\n")


def user_borrowings(bot, message) -> None:
    from borrowing.models import Borrowing
    borrowings_info_queryset = Borrowing.objects.filter(
        user__customer__chat_id=message.chat.id,
        is_active=True
    )
    borrowings_info = "Your borrowings:\n\n" + "\n".join([
        f"-Book:  {borrowing.book}\n"
        f"--Borrow date:  {borrowing.borrow_date}\n"
        f"--Expected return date:  {borrowing.expected_return_date}\n"
        for borrowing in borrowings_info_queryset
    ])

    bot.reply_to(message, borrowings_info)
