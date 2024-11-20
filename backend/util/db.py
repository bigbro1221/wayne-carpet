
from datetime import datetime
import pytz
from util.logger import logger 
tashkent_tz = pytz.timezone("Asia/Tashkent")

# Function to save client profile (specific chat) to Firestore
def save_client_profile(chat_id, user_id, db, language):
    profile_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "language": language,
        "created_at": datetime.now(tashkent_tz).isoformat()
    }
    db.collection("client_profiles").document(str(chat_id)).set(profile_data)

# Function to save chat message to Firestore
def save_chat_log(chat_id, role, message, db):
    logger.info(f"logging chat: {message}")
    log_data = {
        "timestamp": datetime.now(tashkent_tz).isoformat(),
        "role": role,
        "message": message
    }
    db.collection("chat_logs").document(str(chat_id)).collection("messages").add(log_data)
    
    
# Function to save or update a user's profile in Firestore
def save_user_profile(user_id, username, first_name, last_name, db):
    # Define the user data
    user_data = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "created_at": datetime.now(tashkent_tz).isoformat()
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

