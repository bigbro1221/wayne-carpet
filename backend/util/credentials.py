
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

import json
import base64

load_dotenv()

# Set your Telegram bot token and API endpoint URL
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")
WAYNE_CARPET_API_URL = os.getenv("WAYNE_CARPET_API_URL")

firebase_service_account_base64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_BASE64")
if not firebase_service_account_base64:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT_BASE64 is not set in the environment variables.")


# Decode the base64 string to get the JSON content
firebase_service_account_json = json.loads(base64.b64decode(firebase_service_account_base64))

# Initialize Firestore client with direct credentials
db_credentials = service_account.Credentials.from_service_account_info(firebase_service_account_json)


# Define greetings in different languages
greetings = {
    "russian": "Привет! Я ваш помощник по продажам. Чем могу помочь вам сегодня?",
    "uzbek_cyrillic": "Салом! Мен сизнинг сотув бўйича ёрдамчингизман. Бугун сизга қандай ёрдам бера оламан?",
    "uzbek_latin": "Salom! Men sizning sotuv bo‘yicha yordamchingizman. Bugun sizga qanday yordam bera olaman?",
}


# Define language options
LANGUAGE, CHAT = range(2)