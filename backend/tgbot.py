from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from google.cloud import firestore
import requests
from telegram.constants import ParseMode
from dotenv import load_dotenv
from util.formatters import format_content
from util.logger import logger
from util.db import save_chat_log, save_client_profile, save_user_profile
from util.credentials import TELEGRAM_TOKEN, WAYNE_CARPET_API_URL, db_credentials, greetings, LANGUAGE, CHAT

load_dotenv()


db = firestore.Client(credentials=db_credentials)

# Define language selection handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Get client information
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name

    # Save or update user profile in Firestore
    save_user_profile(user_id, username, first_name, last_name, db)

    # Initialize profile in Firestore with no language set yet
    save_client_profile(chat_id, user_id, db, language=None)

    # Display language options as a keyboard with flags
    keyboard = [
        ["🇷🇺 Русский", "🇺🇿 Ўзбекча (Кирил)", "🇺🇿 O'zbekcha (Lotin)"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите язык:", reply_markup=reply_markup)
    
    # Log the language selection prompt in chat logs
    save_chat_log(chat_id, "bot", "Выберите язык:", db)
    
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
    
    save_chat_log(chat_id, "bot", greeting, db)
    
    return CHAT

# Handle chat messages in the selected language
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.text)
    chat_id = update.message.chat_id
    user_message = update.message.text

    # Log the user's message
    save_chat_log(chat_id, "user", user_message, db)

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
        save_chat_log(chat_id, "bot", formatted_content, db)

        # Send the assistant's formatted response back to the user
        await update.message.reply_text(formatted_content, parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        # Handle any errors by notifying the user
        error_message = "An error occurred. Please try again later."
        logger.error(e)
        await update.message.reply_text(error_message)

        # Log the error message
        save_chat_log(chat_id, "bot", error_message, db)

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
