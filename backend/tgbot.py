from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from google.cloud import firestore
from google.oauth2 import service_account
import requests
import os
import re
from telegram.constants import ParseMode
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
import json
import base64
import logging


load_dotenv()

class LogColors:
    RESET = "\033[0m"
    BLUE = "\033[34m"
    ORANGE = "\033[33m"  # Orange is represented as yellow in ANSI
    RED = "\033[31m"

class ColoredFormatter(logging.Formatter):
    LOG_COLORS = {
        logging.INFO: LogColors.BLUE,
        logging.WARNING: LogColors.ORANGE,
        logging.ERROR: LogColors.RED,
    }

    def format(self, record):
        log_color = self.LOG_COLORS.get(record.levelno, LogColors.RESET)
        message = super().format(record)
        return f"{log_color}{message}{LogColors.RESET}"


formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust the level as needed
logger.addHandler(handler)

# Set your Telegram bot token and API endpoint URL
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)


if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")
WAYNE_CARPET_API_URL = os.getenv("WAYNE_CARPET_API_URL")

firebase_service_account_base64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_BASE64")
print(firebase_service_account_base64)
if not firebase_service_account_base64:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT_BASE64 is not set in the environment variables.")

# Decode the base64 string to get the JSON content
firebase_service_account_json = json.loads(base64.b64decode(firebase_service_account_base64))

print(firebase_service_account_json)
# Initialize Firestore client with direct credentials
credentials = service_account.Credentials.from_service_account_info(firebase_service_account_json)

db = firestore.Client(credentials=credentials)

# Define language options
LANGUAGE, CHAT = range(2)


# Define greetings in different languages
greetings = {
    "russian": "Привет! Я ваш помощник по продажам. Чем могу помочь вам сегодня?",
    "uzbek_cyrillic": "Салом! Мен сизнинг сотув бўйича ёрдамчингизман. Бугун сизга қандай ёрдам бера оламан?",
    "uzbek_latin": "Salom! Men sizning sotuv bo‘yicha yordamchingizman. Bugun sizga qanday yordam bera olaman?",
}

def format_content(content):
    # Define special characters for MarkdownV2 that need to be escaped
    special_characters = r'([_*\[\]()~`>#+\-=|{}.!-])'
    
    # Escape special characters with a backslash
    formatted_content = re.sub(special_characters, r'\\\1', content)
    
    # Replace **bold** syntax with MarkdownV2-compatible bold (single *)
    formatted_content = formatted_content.replace("**", "*")
    
    return formatted_content

# Function to save or update a user's profile in Firestore
def save_user_profile(user_id, username, first_name, last_name):
    # Define the user data
    user_data = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "created_at": datetime.now().isoformat()
    }

    # Reference to the user's document
    user_ref = db.collection("users").document(str(user_id))
    
    # Check if the user already exists in Firestore
    if not user_ref.get().exists:
        # Add the new user profile
        user_ref.set(user_data)
    else:
        # Update existing user data if necessary (e.g., username or name changes)
        user_ref.update(user_data)

# Function to save client profile (specific chat) to Firestore
def save_client_profile(chat_id, user_id, language):
    profile_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "language": language,
        "created_at": datetime.now().isoformat()
    }
    db.collection("client_profiles").document(str(chat_id)).set(profile_data)

# Function to save chat message to Firestore
def save_chat_log(chat_id, role, message):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "message": message
    }
    db.collection("chat_logs").document(str(chat_id)).collection("messages").add(log_data)

# Define language selection handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Get client information
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name

    # Save or update user profile in Firestore
    save_user_profile(user_id, username, first_name, last_name)

    # Initialize profile in Firestore with no language set yet
    save_client_profile(chat_id, user_id, language=None)

    # Display language options as a keyboard with flags
    keyboard = [
        ["🇷🇺 Русский", "🇺🇿 Ўзбекча (Кирил)", "🇺🇿 O'zbekcha (Lotin)"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите язык:", reply_markup=reply_markup)
    
    # Log the language selection prompt in chat logs
    save_chat_log(chat_id, "bot", "Выберите язык:")
    
    return LANGUAGE

# Store the chosen language and greet the user
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat_id
    chosen_language = update.message.text.lower()

    # Update client profile with the chosen language
    db.collection("client_profiles").document(str(chat_id)).update({"language": chosen_language})

    # Determine which greeting to use
    if chosen_language == "🇷🇺 русский":
        greeting = greetings["russian"]
    elif chosen_language == "🇺🇿 ўзбекча (кирил)":
        greeting = greetings["uzbek_cyrillic"]
    elif chosen_language == "🇺🇿 o'zbekcha (lotin)":
        greeting = greetings["uzbek_latin"]
    else:
        greeting = "Hello! I'm your assistant. How can I help you today?"

    # Send greeting and log it
    await update.message.reply_text(greeting, reply_markup=ReplyKeyboardRemove())
    
    save_chat_log(chat_id, "bot", greeting)
    
    return CHAT

# Handle chat messages in the selected language
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.text)
    chat_id = update.message.chat_id
    user_message = update.message.text

    # Log the user's message
    save_chat_log(chat_id, "user", user_message)

    try:
        # Send the user's message to the FastAPI chat endpoint
        response = requests.post(WAYNE_CARPET_API_URL, json={"message": user_message})
        response_data = response.json()

        # Check if 'response' is present in the returned JSON
        assistant_response = response_data.get("response", {})
        content = assistant_response.get("content", "I'm here to assist you, but I encountered an issue understanding that.")

        # Format content for Telegram (Cyrillic-friendly and Markdown formatting)
        formatted_content = format_content(content)

        # Log the bot's response
        save_chat_log(chat_id, "bot", formatted_content)

        # Send the assistant's formatted response back to the user
        await update.message.reply_text(formatted_content, parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        # Handle any errors by notifying the user
        error_message = "An error occurred. Please try again later."
        logger.error(e)
        await update.message.reply_text(error_message)

        # Log the error message
        save_chat_log(chat_id, "bot", error_message)

# Define the conversation handler
def main():
    # Initialize the Telegram bot application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    
    # Set up the conversation handler with states for LANGUAGE and CHAT
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Register the conversation handler
    app.add_handler(conv_handler)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling for updates
    app.run_polling()

if __name__ == "__main__":
    main()
