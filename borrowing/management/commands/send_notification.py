import requests
from django.conf import settings


def notification(message):
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    print("DATA", data)
    requests.post(url, data)
    # response = requests.post(url, json=data)
    # print("RESPONSE HEREEEEEEEEEEEEEEEEEEEEEEEEE", response, response.content)
    # print("RESPONSE DATA", response.json())

def get_updates():
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    updates = response.json()
    print("Обновления:", updates)


# Вызовите эту функцию, чтобы увидеть обновления
# print("UPDATESSSSSSSSSSSSSSSSSSSSSSS", get_updates())
