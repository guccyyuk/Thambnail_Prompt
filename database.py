"""
Simple in-memory database (no MongoDB required)
For production, replace with actual database
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# In-memory storage
users = {}
prompts = {}
poster_formats = {}
welcome_data = None

def get_user(user_id):
    """Get user by ID"""
    return users.get(user_id)

def create_user(user_id, username, first_name):
    """Create new user"""
    user = {
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'created_at': datetime.now()
    }
    users[user_id] = user
    logger.info(f"✅ User created: {user_id} - {first_name}")
    return user

def save_prompt(user_id, prompt_name, prompt_text):
    """Save user prompt"""
    if user_id not in prompts:
        prompts[user_id] = []
    
    prompts[user_id].append({
        'prompt_name': prompt_name,
        'prompt_text': prompt_text,
        'created_at': datetime.now(),
        '_id': f"{user_id}_{len(prompts[user_id])}"
    })
    logger.info(f"✅ Prompt saved: {user_id} - {prompt_name}")

def get_user_prompts(user_id):
    """Get all user prompts"""
    return prompts.get(user_id, [])

def delete_prompt(user_id, prompt_name):
    """Delete user prompt"""
    if user_id in prompts:
        prompts[user_id] = [p for p in prompts[user_id] if p['prompt_name'] != prompt_name]
        logger.info(f"✅ Prompt deleted: {user_id} - {prompt_name}")

def save_poster_format(user_id, format_text):
    """Save poster format"""
    poster_formats[user_id] = {
        'format_text': format_text,
        'updated_at': datetime.now()
    }
    logger.info(f"✅ Poster format saved: {user_id}")

def get_poster_format(user_id):
    """Get poster format"""
    result = poster_formats.get(user_id)
    return result['format_text'] if result else None

def save_welcome_message(welcome_text, media_id=None, media_type=None, buttons=None):
    """Save welcome message"""
    global welcome_data
    welcome_data = {
        'text': welcome_text,
        'media_id': media_id,
        'media_type': media_type,
        'buttons': buttons,
        'updated_at': datetime.now()
    }
    logger.info("✅ Welcome message saved")

def get_welcome_message():
    """Get welcome message"""
    return welcome_data
