---
title: Thumbnail Generator Bot
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# 🎬 Thumbnail Generator Bot

Professional anime thumbnail creator bot for Telegram.

## ✨ Features

- 🎯 AI-powered best scene detection
- 🖼️ Professional 1920x1080 thumbnails
- 🏷️ Automatic EPISODE tags & HINDI ribbons
- 📝 Custom poster creation
- 🎨 Auto anime name detection
- 🔄 Refresh option for more scenes
- 👥 Group support (owner only)

## 🚀 Quick Start

### 1. Create HuggingFace Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Name: `thumbnailgenreter`
4. SDK: **Docker** (IMPORTANT!)
5. Click "Create Space"

### 2. Upload Files

Upload all these files to your space:
- app.py
- bot.py
- config.py
- database.py
- video_processor.py
- thumbnail_creator.py
- admin_panel.py
- requirements.txt
- Dockerfile
- README.md

### 3. Set Environment Variables

Go to Settings → Variables and secrets, add:

```
BOT_TOKEN=your_bot_token_from_botfather
MONGODB_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
OWNER_ID=your_telegram_user_id
WEBHOOK_URL=https://YOUR_USERNAME-thumbnailgenreter.hf.space/webhook
```

**IMPORTANT:** Replace `YOUR_USERNAME` with your HuggingFace username in WEBHOOK_URL!

Example:
```
WEBHOOK_URL=https://guccyyuk-thumbnailgenreter.hf.space/webhook
```

### 4. Wait for Build

Space will build automatically (5-10 minutes). Check logs for:
```
✅ Webhook set: https://...
✅ Bot started successfully!
```

### 5. Test Your Bot

1. Open your Telegram bot
2. Send `/start`
3. Send an anime video
4. Select best scene
5. Get professional thumbnail!

## 📱 Commands

- `/start` - Start bot
- `/help` - Show help
- `/setposter` - Set poster format
- `/adminpanel` - Admin settings (owner only)
- `/createthumbnail` - Use in groups (owner only)

## 🔧 Technical Details

**Architecture:**
- **Frontend:** Flask (lightweight webhook server)
- **Bot:** python-telegram-bot (webhook mode)
- **AI:** Google Gemini (scene analysis)
- **Image Processing:** OpenCV + Pillow
- **Database:** MongoDB

**Why Webhook?**
- ✅ Faster response time
- ✅ No timeout issues
- ✅ Better for HuggingFace
- ✅ Production-ready

**Why No Gradio?**
- ❌ Dependency conflicts
- ❌ Unnecessary overhead
- ❌ Polling doesn't work well
- ✅ Flask is simpler & faster

## 🐛 Troubleshooting

### Bot not responding?

1. Check logs for errors
2. Verify WEBHOOK_URL is correct
3. Visit `/setwebhook` endpoint to reset
4. Check all secrets are set

### Video processing fails?

1. Ensure video is < 50MB
2. Check GEMINI_API_KEY is valid
3. Try different video format

### Webhook not working?

1. Space URL format: `https://USERNAME-SPACENAME.hf.space/webhook`
2. Visit `/health` to check bot status
3. Rebuild space if needed

## 📊 How It Works

```
User sends video
    ↓
Bot downloads to temp_files/
    ↓
OpenCV extracts frames
    ↓
Gemini AI analyzes quality
    ↓
Top 10 scenes sent to user
    ↓
User selects + episode number
    ↓
Pillow creates thumbnail:
  - Enhance colors/sharpness
  - Add EPISODE text (yellow)
  - Add HINDI ribbon (diagonal)
  - Resize to 1920x1080
    ↓
Thumbnail ready! 🎉
```

## 🎨 Poster Format

Example format for `/setposter`:

```
⛩ {AnimeName}
╭───────────────────
├ ✨ Ratings - {Rating} IMDB
├ ❄️ Season - {Season}
├ 🎬 Episodes - {Episodes}
├ 🔈 Audio - {Audio}
├ 📸 Quality - {Quality}
├ 🎭 Genres - {Genres}
├───────────────────
• 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆: @YourChannel
```

Variables like `{AnimeName}`, `{Rating}` auto-replace!

## 💡 Pro Tips

1. **Better Detection:** Use clear anime names in video filenames
2. **High Quality:** HD videos = better thumbnails
3. **More Scenes:** Use refresh button unlimited times
4. **Group Use:** Add bot as admin, use `/createthumbnail`

## 📝 License

MIT License - Free to use and modify!

## 👨‍💻 Creator

Made with ❤️ by [@obito_space](https://t.me/obito_space)

## 🙏 Credits

- Telegram Bot API
- Google Gemini AI
- OpenCV
- MongoDB
- HuggingFace Spaces

---

**Need Help?** Contact [@obito_space](https://t.me/obito_space) on Telegram!
