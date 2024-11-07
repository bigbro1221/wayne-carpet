import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from pathlib import Path
import shutil
from pydantic import BaseModel
from google.cloud import aiplatform
from typing import Optional
from openai import OpenAI
import json
import re 
from firebase_admin import credentials
from firebase_admin import firestore

app = FastAPI()
origins = ["http://localhost:3000"]  # React app runs on port 3000 by default
client = OpenAI(api_key="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")

class FineTuneRequest(BaseModel):
    file_id: str
    model: str = "gpt-4o-mini-2024-07-18"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    user_id: str
    username: str
    first_name: str
    last_name: str

# Directory to store uploaded datasets
DATASET_DIR = Path("datasets")
DATASET_DIR.mkdir(exist_ok=True)
# Initialize Firestore client


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./firebase_account_key.json" 

cred = credentials.Certificate('./firebase_account_key.json')
firebase_admin.initialize_app(cred)
db = firestore.Client()

class ChatMessage(BaseModel):
    message: str

class FineTuneConfig(BaseModel):
    learning_rate: Optional[float] = 0.001
    batch_size: Optional[int] = 16
    epochs: Optional[int] = 3
    dataset_path: str  # Path of the uploaded dataset

def load_instructions(filename="datasets/pre-training.jsonl"):
    """Load assistant instructions from pre-training.jsonl."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            return entry["completion"]  # Assume single instruction entry


def load_qas(filename="datasets/ultimate.jsonl"):
    """Load Q&A pairs from ultimate.jsonl and format as text."""
    qas_text = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            qas_text.append(f"Q: {entry['prompt']}\nA: {entry['completion']}")
    return "\n\n".join(qas_text)

instructions = load_instructions("datasets/pre-training.jsonl")
qas_content = load_qas("datasets/ultimate.jsonl")
system_message_content = f"{instructions}\n\nHere are some example questions and answers:\n\n{qas_content}"

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot Backend!"}

@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    # Ensure it's a JSONL file
    if not file.filename.endswith(".jsonl"):
        raise HTTPException(status_code=400, detail="Only .jsonl files are accepted")

    # Save the file to the dataset directory
    file_path = DATASET_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Dataset uploaded successfully", "file_path": str(file_path)}

# Endpoint to get business info from Firestore
@app.get("/business_info")
async def get_business_info():
    doc_ref = db.collection("configurations").document("business_info")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        raise HTTPException(status_code=404, detail="Business info not found")

@app.post("/chat")
async def chat(data: ChatMessage):
    try:
            
        system_message = {"role": "system", "content": system_message_content}

        # User's message
        user_message = {"role": "user", "content": data.message}
        # Define the system message with combined instructions and examples
        print(data.message)
        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system_message, user_message]
        )
        
        reply = completion.choices[0].message
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Example endpoint to get users
@app.get("/api/users")
async def get_users():
    all_docs = []
    docs = db.collection("users").stream()
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data["id"] = doc.id  # Add the document ID if needed
        all_docs.append(doc_data)
    
    # Check if we have documents; if not, return a 404 error
    if not all_docs:
        raise HTTPException(status_code=404, detail="No documents found in users")

    return all_docs

from datetime import datetime


def format_content(content):
    # Define special characters for MarkdownV2 that need to be escaped
    
    
    # Escape special characters with a backslash
    
    # Replace **bold** syntax with MarkdownV2-compatible bold (single *)
    formatted_content = content.replace("**", "*").replace("\\", "")
    
    return formatted_content

@app.get("/api/chat-logs")
async def get_chat_logs():

    db = firestore.Client()
    grouped_chats = []

    # Retrieve all users
    users = db.collection("users").stream()
    
    # Loop through each user and get their chat logs
    for user in users:
        user_data = user.to_dict()
        user_id = user.id

        # Initialize a list to store each user's chat logs and track last interaction time
        user_chat_logs = []
        last_interaction = None

        # Access the user's chat logs in chat_logs collection by user_id
        chat_doc_ref = db.collection("chat_logs").document(user_id)
        messages_collection_ref = chat_doc_ref.collection("messages")
        
        # Retrieve all messages for the user in the messages subcollection, ordered by timestamp ASC
        messages = messages_collection_ref.order_by("timestamp", direction=firestore.Query.ASCENDING).stream()
        
        # Loop through each message to append it to user_chat_logs and track the latest timestamp
        for message in messages:
            message_data = message.to_dict()
            message_data["message"] = format_content(message_data.get("message", ""))    
            message_data["message_id"] = message.id  # Optionally add message ID
            user_chat_logs.append(message_data)

            # Update last interaction to the timestamp of the latest message
            message_timestamp = message_data.get("timestamp")
            if message_timestamp:
                # Parse timestamp if it’s in string format
                message_timestamp = datetime.fromisoformat(message_timestamp) if isinstance(message_timestamp, str) else message_timestamp
                last_interaction = max(last_interaction, message_timestamp) if last_interaction else message_timestamp

        # Add user data and chat logs if any messages exist
        if user_chat_logs:
            grouped_chats.append({
                "user": {
                    "user_id": user_id,
                    **user_data
                },
                "chat_logs": user_chat_logs,
                "last_interaction": last_interaction  # Store last interaction for sorting
            })

    # Sort grouped_chats by last interaction timestamp DESC
    grouped_chats.sort(key=lambda x: x["last_interaction"], reverse=True)

    # Remove last_interaction from the response for cleaner output
    for entry in grouped_chats:
        entry.pop("last_interaction", None)

    return grouped_chats


@app.get("/api/chat-logs/{user_id}/messages")
async def get_user_messages(user_id: str):
    messages_ref = db.collection("chat_logs").document(user_id).collection("messages")
    messages = [msg.to_dict() for msg in messages_ref.stream()]

    # Apply format_content to each message's "message" field
    for msg in messages:
        msg["message"] = "bruh"
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this user")

    return messages
