import os
from dotenv import load_dotenv

load_dotenv()

# Bot credentials
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OWNER_ID = int(os.getenv('OWNER_ID', 0))

# Webhook URL (set this in HuggingFace secrets)
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

# File storage
TEMP_DIR = "temp_files"
OUTPUT_DIR = "outputs"

# Create directories
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
