import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from config import *
from database import *
from video_processor import extract_key_frames, extract_anime_name_from_text
from thumbnail_creator import create_thumbnail, create_poster
from admin_panel import get_admin_panel_markup, get_welcome_edit_markup

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User states
user_states = {}
temp_data = {}

class BotStates:
    WAITING_EPISODE = "waiting_episode"
    WAITING_PROMPT_NAME = "waiting_prompt_name"
    WAITING_PROMPT_TEXT = "waiting_prompt_text"
    WAITING_POSTER_FORMAT = "waiting_poster_format"
    WAITING_WELCOME_TEXT = "waiting_welcome_text"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with custom welcome"""
    user = update.effective_user
    
    if not get_user(user.id):
        create_user(user.id, user.username, user.first_name)
        logger.info(f"✅ New user: {user.id} - {user.first_name}")
    
    welcome = get_welcome_message()
    
    if welcome and welcome.get('text'):
        text = welcome['text'].replace('{nickname}', user.first_name or 'User')
        text = text.replace('{username}', f"@{user.username}" if user.username else 'User')
        
        keyboard = []
        if welcome.get('buttons'):
            for btn in welcome['buttons']:
                keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        try:
            if welcome.get('media_id') and welcome.get('media_type'):
                if welcome['media_type'] == 'photo':
                    await update.message.reply_photo(
                        welcome['media_id'], 
                        caption=text, 
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                elif welcome['media_type'] == 'video':
                    await update.message.reply_video(
                        welcome['media_id'], 
                        caption=text, 
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                return
        except Exception as e:
            logger.error(f"❌ Welcome media error: {e}")
    
    # Default welcome
    default_text = f"""
🎬 **Namaste {user.first_name}!**

Main **Thumbnail Generator Bot** hun! 🎨

**Kya kar sakta hun?**
✨ Video se best scenes extract karta hun
🖼️ Professional anime thumbnails banata hun  
📝 Custom posters with episode info
🎯 Automatic anime name detection

**Quick Start:**
📹 Mujhe ek anime video bhejo
⏳ Main 10 best scenes dikhaunga
✅ Select karo aur thumbnail ready!

**Commands:**
/help - Detailed help
/setposter - Poster format customize karo

Bot by @obito_space 💫
"""
    
    await update.message.reply_text(default_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed help"""
    help_text = """
🎬 **Thumbnail Generator Bot - Complete Guide**

**━━━━━ Basic Usage ━━━━━**

1️⃣ **Video Bhejo** → Bot process karega
2️⃣ **10 Scenes Milenge** → Best quality frames
3️⃣ **Select Karo** → Jo scene pasand aaye
4️⃣ **Episode Number** → Thumbnail ban jayega!

**━━━━━ Commands ━━━━━**

📌 /start - Bot start karo
📌 /help - Ye help message
📝 /setposter - Poster format set
👑 /adminpanel - Admin panel (owner only)
🎬 /createthumbnail - Group use (owner only)

**━━━━━ Features ━━━━━**

✨ Auto anime name detection
🎯 AI-powered scene selection
🖼️ Professional EPISODE tags
🏷️ HINDI ribbon automatic
📊 High quality 1920x1080
🎨 Enhanced colors & sharpness

**Support:** @obito_space
**Made with ❤️**
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads - main feature"""
    user = update.effective_user
    message = update.message
    
    # Group check - only owner can use in groups
    if message.chat.type in ['group', 'supergroup']:
        if user.id != OWNER_ID:
            return
        
        # Must reply to /createthumbnail command
        if not (message.reply_to_message and 
                message.reply_to_message.text and 
                '/createthumbnail' in message.reply_to_message.text):
            return
    
    status_msg = await message.reply_text(
        "📥 **Video download ho raha hai...**\n⏳ Thoda wait karo!",
        parse_mode='Markdown'
    )
    
    try:
        # Download video
        video_file = await message.video.get_file()
        video_path = os.path.join(TEMP_DIR, f"{user.id}_video.mp4")
        
        await video_file.download_to_drive(video_path)
        logger.info(f"📹 Video downloaded: {user.id}")
        
        await status_msg.edit_text(
            "🔍 **AI se best scenes dhoondh raha hun...**\n🎯 Patience rakh!",
            parse_mode='Markdown'
        )
        
        # Extract key frames using AI
        frame_paths = extract_key_frames(video_path, num_frames=10)
        
        if not frame_paths:
            await status_msg.edit_text(
                "❌ **Sorry yaar! Koi achha scene nahi mila.**\n\n"
                "💡 Dusri video try karo - clear aur high quality!",
                parse_mode='Markdown'
            )
            return
        
        await status_msg.edit_text(
            f"✅ **{len(frame_paths)} scenes ready!**\n"
            f"👇 Neeche dekho aur best wala select karo!",
            parse_mode='Markdown'
        )
        
        # Send frames with selection buttons
        keyboard = []
        for i, frame_path in enumerate(frame_paths, 1):
            try:
                with open(frame_path, 'rb') as f:
                    await message.reply_photo(
                        f, 
                        caption=f"🎬 **Scene #{i}** - High Quality Frame",
                        parse_mode='Markdown'
                    )
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ Scene {i} Select Karo", 
                        callback_data=f"select_frame_{i}"
                    )
                ])
            except Exception as e:
                logger.error(f"❌ Frame send error: {e}")
        
        # Refresh button
        keyboard.append([
            InlineKeyboardButton(
                "🔄 Refresh - Aur Scenes Dikhao", 
                callback_data="refresh_frames"
            )
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            "🎯 **Kaunsa scene best laga?**\n\n"
            "👆 Button pe click karke select karo!\n"
            "🔄 Agar ye scenes achhe nahi, toh Refresh karo!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Store data for later use
        caption_text = message.caption or message.video.file_name or ""
        temp_data[user.id] = {
            'frame_paths': frame_paths,
            'video_path': video_path,
            'caption': caption_text
        }
        
        # Extract anime name from caption/filename
        anime_name = extract_anime_name_from_text(caption_text)
        if anime_name:
            temp_data[user.id]['anime_name'] = anime_name
            logger.info(f"🎬 Anime detected: {anime_name}")
        
    except Exception as e:
        logger.error(f"❌ Video processing error: {e}")
        await status_msg.edit_text(
            f"❌ **Kuch problem ho gayi!**\n\n"
            f"**Error:** {str(e)}\n\n"
            f"💡 Fir se try karo ya @obito_space ko batao!",
            parse_mode='Markdown'
        )
        
        # Cleanup
        if user.id in temp_data:
            del temp_data[user.id]

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Frame selection
    if data.startswith("select_frame_"):
        frame_num = int(data.split("_")[2])
        
        if user_id not in temp_data:
            await query.edit_message_text(
                "❌ **Session expire ho gaya!**\n"
                "🔄 Fir se video bhejo.",
                parse_mode='Markdown'
            )
            return
        
        await query.edit_message_text(
            f"🎨 **Scene {frame_num} selected!**\n"
            f"✨ Thumbnail ban raha hai...\n"
            f"⏳ Bas kuch seconds!",
            parse_mode='Markdown'
        )
        
        # Ask for episode number
        await query.message.reply_text(
            "📝 **Episode number batao:**\n\n"
            "Example: 1, 2, 3, 10, etc.\n"
            "🔢 Sirf number bhejo!",
            parse_mode='Markdown'
        )
        
        user_states[user_id] = f"{BotStates.WAITING_EPISODE}_{frame_num}"
    
    # Refresh frames
    elif data == "refresh_frames":
        if user_id not in temp_data:
            await query.edit_message_text(
                "❌ **Session expire ho gaya!**\n"
                "🔄 Fir se video bhejo.",
                parse_mode='Markdown'
            )
            return
        
        await query.edit_message_text(
            "🔄 **Naye scenes dhoondh raha hun...**\n⏳ Wait karo!",
            parse_mode='Markdown'
        )
        
        try:
            video_path = temp_data[user_id]['video_path']
            frame_paths = extract_key_frames(video_path, num_frames=10)
            
            if not frame_paths:
                await query.message.reply_text("❌ Naye scenes nahi mile!")
                return
            
            temp_data[user_id]['frame_paths'] = frame_paths
            
            # Send new frames
            keyboard = []
            for i, frame_path in enumerate(frame_paths, 1):
                with open(frame_path, 'rb') as f:
                    await query.message.reply_photo(
                        f, 
                        caption=f"🎬 **New Scene #{i}**",
                        parse_mode='Markdown'
                    )
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ Scene {i} Select", 
                        callback_data=f"select_frame_{i}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton(
                    "🔄 Aur Refresh", 
                    callback_data="refresh_frames"
                )
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "🆕 **Naye scenes ready!**\n\n"
                "👆 Ab select karo best wala!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Refresh error: {e}")
            await query.message.reply_text(
                f"❌ **Error:** {str(e)}",
                parse_mode='Markdown'
            )
    
    # Create poster
    elif data.startswith("create_poster_"):
        episode_num = data.split("_")[2]
        
        if user_id not in temp_data or 'last_thumbnail' not in temp_data[user_id]:
            await query.answer("❌ Thumbnail nahi mila!", show_alert=True)
            return
        
        await query.edit_message_text(
            "📄 **Poster ban raha hai...**\n✨ Professional look de raha hun!",
            parse_mode='Markdown'
        )
        
        try:
            poster_format = get_poster_format(user_id)
            if not poster_format:
                await query.message.reply_text(
                    "❌ **Pehle poster format set karo!**\n\n"
                    "Use: /setposter",
                    parse_mode='Markdown'
                )
                return
            
            anime_name = temp_data[user_id].get('anime_name', 'Unknown Anime')
            thumbnail_path = temp_data[user_id]['last_thumbnail']
            
            poster_path = create_poster(thumbnail_path, anime_name, poster_format)
            
            with open(poster_path, 'rb') as f:
                await query.message.reply_photo(
                    f, 
                    caption=(
                        f"✅ **Poster Ready!**\n\n"
                        f"🎬 {anime_name}\n"
                        f"📺 Episode {episode_num}"
                    ),
                    parse_mode='Markdown'
                )
            
            await query.message.reply_text("🎉 **Poster ban gaya! Enjoy!** 🔥")
            
        except Exception as e:
            logger.error(f"❌ Poster creation error: {e}")
            await query.message.reply_text(
                f"❌ **Poster error:** {str(e)}",
                parse_mode='Markdown'
            )
    
    # Admin panel
    elif data == "admin_panel":
        if user_id != OWNER_ID:
            await query.answer("❌ Only owner access!", show_alert=True)
            return
        
        await query.edit_message_text(
            "⚙️ **Admin Panel**\n\nManage bot settings:",
            reply_markup=get_admin_panel_markup(),
            parse_mode='Markdown'
        )
    
    elif data == "admin_setwelcome":
        if user_id != OWNER_ID:
            await query.answer("❌ Only owner!", show_alert=True)
            return
        
        current_welcome = get_welcome_message()
        if current_welcome and current_welcome.get('text'):
            await query.edit_message_text(
                f"📝 **Current Welcome:**\n\n{current_welcome['text']}\n\n"
                f"Edit karna hai?",
                reply_markup=get_welcome_edit_markup(),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("📝 Welcome message type karo:")
            user_states[user_id] = BotStates.WAITING_WELCOME_TEXT
    
    elif data == "welcome_edit_text":
        await query.edit_message_text("✏️ Naya welcome message type karo:")
        user_states[user_id] = BotStates.WAITING_WELCOME_TEXT
    
    elif data == "welcome_remove":
        save_welcome_message("Default welcome removed")
        await query.edit_message_text("✅ Welcome message removed!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages based on user state"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_states:
        return
    
    state = user_states[user_id]
    
    # Episode number input
    if state.startswith(BotStates.WAITING_EPISODE):
        try:
            episode_num = int(text)
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid number!**\n\n"
                "🔢 Sirf number bhejo: 1, 2, 3, etc.",
                parse_mode='Markdown'
            )
            return
        
        frame_num = int(state.split("_")[1])
        
        if user_id not in temp_data:
            await update.message.reply_text(
                "❌ **Session expire!** Fir se video bhejo.",
                parse_mode='Markdown'
            )
            return
        
        status_msg = await update.message.reply_text(
            "🎨 **Professional thumbnail ban raha hai...**\n\n"
            "✨ Colors enhance ho rahe\n"
            "🎯 EPISODE tag add ho raha\n"
            "🏷️ HINDI ribbon lag raha\n"
            "⏳ Bas kuch seconds...",
            parse_mode='Markdown'
        )
        
        try:
            frame_path = temp_data[user_id]['frame_paths'][frame_num - 1]
            output_path = create_thumbnail(frame_path, episode_num)
            
            anime_name = temp_data[user_id].get('anime_name', 'Unknown Anime')
            
            with open(output_path, 'rb') as f:
                await update.message.reply_photo(
                    f, 
                    caption=(
                        f"✅ **Thumbnail Ready!**\n\n"
                        f"🎬 Anime: **{anime_name}**\n"
                        f"📺 Episode: **{episode_num}**\n"
                        f"📐 Resolution: **1920x1080**\n"
                        f"✨ Quality: **Professional**\n\n"
                        f"Made with ❤️ by Thumbnail Bot"
                    ),
                    parse_mode='Markdown'
                )
            
            await status_msg.delete()
            
            # Poster option
            keyboard = [[
                InlineKeyboardButton(
                    "📄 Poster Bhi Banao", 
                    callback_data=f"create_poster_{episode_num}"
                )
            ]]
            await update.message.reply_text(
                "🎉 **Thumbnail ready!**\n\nPoster bhi banana hai?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            temp_data[user_id]['last_thumbnail'] = output_path
            del user_states[user_id]
            
        except Exception as e:
            logger.error(f"❌ Thumbnail creation error: {e}")
            await status_msg.edit_text(
                f"❌ **Error:** {str(e)}",
                parse_mode='Markdown'
            )
    
    # Welcome message input
    elif state == BotStates.WAITING_WELCOME_TEXT:
        save_welcome_message(text)
        await update.message.reply_text("✅ **Welcome message saved!**", parse_mode='Markdown')
        del user_states[user_id]
    
    # Poster format input
    elif state == BotStates.WAITING_POSTER_FORMAT:
        save_poster_format(user_id, text)
        await update.message.reply_text(
            "✅ **Poster format saved!**\n\n"
            "Ab /poster use kar sakte ho!",
            parse_mode='Markdown'
        )
        del user_states[user_id]

async def setposter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set poster format"""
    example_format = """⛩ {AnimeName}
╭───────────────────
├ ✨ Ratings - {Rating} IMDB
├ ❄️ Season - {Season}
├ 🎬 Episodes - {Episodes}
├ 🔈 Audio - {Audio}
├ 📸 Quality - {Quality}
├ 🎭 Genres - {Genres}
├───────────────────
• 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆: @CrunchyRollChannel"""
    
    await update.message.reply_text(
        "📝 **Poster Format Set Karo:**\n\n"
        f"**Example:**\n```\n{example_format}\n```\n\n"
        "💡 {AnimeName}, {Rating} etc. automatically change honge!\n\n"
        "Ab apna format paste karo:",
        parse_mode='Markdown'
    )
    
    user_states[update.effective_user.id] = BotStates.WAITING_POSTER_FORMAT

async def adminpanel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel access"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only owner can access!")
        return
    
    await update.message.reply_text(
        "⚙️ **Admin Panel**",
        reply_markup=get_admin_panel_markup(),
        parse_mode='Markdown'
    )

async def createthumbnail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Group thumbnail creation command"""
    if update.effective_user.id != OWNER_ID:
        return
    
    if update.message.chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(
            "❌ Ye command sirf groups mein kaam karta hai!"
        )
        return
    
    await update.message.reply_text(
        "👌 **Ab video ko reply mein bhejo!**\n"
        "📹 Is message ko reply karo with video."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler"""
    logger.error(f"❌ Exception: {context.error}")
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ **Kuch error aaya!**\n\n"
            f"Error: {str(context.error)}\n\n"
            "Fir se try karo ya @obito_space ko batao!"
        )

def create_application():
    """Create and configure bot application"""
    logger.info("🚀 Creating bot application...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setposter", setposter_command))
    application.add_handler(CommandHandler("adminpanel", adminpanel_command))
    application.add_handler(CommandHandler("createthumbnail", createthumbnail_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot application created successfully!")
    return application
