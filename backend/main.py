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
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()
origins = ["http://localhost:3000"]  # React app runs on port 3000 by default

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
