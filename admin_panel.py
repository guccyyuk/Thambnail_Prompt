from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_panel_markup():
    """Get admin panel keyboard"""
    keyboard = [
        [InlineKeyboardButton("📝 Set Welcome Message", callback_data="admin_setwelcome")],
        [InlineKeyboardButton("📊 View Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 User List", callback_data="admin_users")],
        [InlineKeyboardButton("🔄 Refresh Prompts", callback_data="admin_refresh_prompts")],
        [InlineKeyboardButton("❌ Close", callback_data="admin_close")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_welcome_edit_markup():
    """Get welcome message edit keyboard"""
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Text", callback_data="welcome_edit_text")],
        [InlineKeyboardButton("🖼️ Edit Media", callback_data="welcome_edit_media")],
        [InlineKeyboardButton("🔘 Set Buttons", callback_data="welcome_set_buttons")],
        [InlineKeyboardButton("🗑️ Remove", callback_data="welcome_remove")],
        [InlineKeyboardButton("◀️ Back", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)