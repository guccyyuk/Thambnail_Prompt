from pymongo import MongoClient
from config import MONGODB_URI
from datetime import datetime

client = MongoClient(MONGODB_URI)
db = client['thumbnail_bot']

users_col = db['users']
prompts_col = db['prompts']
poster_formats_col = db['poster_formats']
welcome_col = db['welcome_messages']

def get_user(user_id):
    return users_col.find_one({'user_id': user_id})

def create_user(user_id, username, first_name):
    user = {
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'created_at': datetime.now()
    }
    users_col.insert_one(user)
    return user

def save_prompt(user_id, prompt_name, prompt_text):
    prompt = {
        'user_id': user_id,
        'prompt_name': prompt_name,
        'prompt_text': prompt_text,
        'created_at': datetime.now()
    }
    prompts_col.insert_one(prompt)

def get_user_prompts(user_id):
    return list(prompts_col.find({'user_id': user_id}))

def delete_prompt(user_id, prompt_name):
    prompts_col.delete_one({'user_id': user_id, 'prompt_name': prompt_name})

def save_poster_format(user_id, format_text):
    poster_formats_col.update_one(
        {'user_id': user_id},
        {'$set': {'format_text': format_text, 'updated_at': datetime.now()}},
        upsert=True
    )

def get_poster_format(user_id):
    result = poster_formats_col.find_one({'user_id': user_id})
    return result['format_text'] if result else None

def save_welcome_message(welcome_text, media_id=None, media_type=None, buttons=None):
    welcome_col.update_one(
        {'_id': 'welcome'},
        {'$set': {
            'text': welcome_text,
            'media_id': media_id,
            'media_type': media_type,
            'buttons': buttons,
            'updated_at': datetime.now()
        }},
        upsert=True
    )

def get_welcome_message():
    return welcome_col.find_one({'_id': 'welcome'})