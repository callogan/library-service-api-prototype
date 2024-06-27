import requests

TOKEN = "6648421266:AAENIpyz0lWFq2ke_dBym0HjrCh9GKEkl40"
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(URL)
updates = response.json()

for update in updates['result']:
    user_id = update['message']['from']['id']
    chat_id = update['message']['chat']['id']
    print(f"User ID: {user_id}")
    print(f"Chat ID: {chat_id}")
