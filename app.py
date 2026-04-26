from flask import Flask, request, jsonify
import asyncio
import logging
from telegram import Update
from bot import create_application
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Bot application (lazy initialization)
bot_app = None
bot_initialized = False

async def init_bot():
    """Initialize bot and set webhook (lazy - only when first request comes)"""
    global bot_app, bot_initialized
    
    if bot_initialized:
        return bot_app
    
    logger.info("🚀 Initializing bot (first request)...")
    
    bot_app = create_application()
    await bot_app.initialize()
    
    webhook_url = os.getenv('WEBHOOK_URL', '')
    if webhook_url:
        try:
            await bot_app.bot.set_webhook(url=webhook_url)
            logger.info(f"✅ Webhook set: {webhook_url}")
        except Exception as e:
            logger.warning(f"⚠️ Webhook setup failed (will retry): {e}")
    else:
        logger.warning("⚠️ WEBHOOK_URL not set! Add it in HuggingFace secrets.")
    
    await bot_app.start()
    bot_initialized = True
    logger.info("✅ Bot initialized successfully!")
    
    return bot_app

@app.route('/')
def home():
    """Home endpoint - shows bot status"""
    return """
    <html>
    <head>
        <title>Thumbnail Generator Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                background: rgba(255,255,255,0.1);
                padding: 50px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3em; margin: 0; }
            .status { 
                font-size: 1.5em; 
                margin: 20px 0;
                color: #4ade80;
            }
            .info {
                font-size: 1em;
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Thumbnail Generator Bot</h1>
            <div class="status">✅ Bot is Running (Webhook Mode)</div>
            <div class="info">
                <p>📱 Open your Telegram bot and send /start</p>
                <p>🎥 Send anime video to create thumbnails</p>
                <p>Made with ❤️ by @obito_space</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    try:
        # Get update from Telegram
        update_data = request.get_json(force=True)
        
        # Initialize bot if not done yet (lazy init)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app_instance = loop.run_until_complete(init_bot())
        
        # Process update
        update = Update.de_json(update_data, app_instance.bot)
        loop.run_until_complete(app_instance.process_update(update))
        loop.close()
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot": "ready" if bot_initialized else "not_initialized",
        "mode": "webhook"
    }), 200

@app.route('/setwebhook')
def set_webhook_manually():
    """Manual webhook setup endpoint"""
    try:
        webhook_url = os.getenv('WEBHOOK_URL', '')
        if not webhook_url:
            return jsonify({
                "status": "error",
                "message": "WEBHOOK_URL not set in environment"
            }), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app_instance = loop.run_until_complete(init_bot())
        loop.run_until_complete(app_instance.bot.set_webhook(url=webhook_url))
        loop.close()
        
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Run Flask app
    port = int(os.getenv('PORT', 7860))
    logger.info(f"🚀 Starting Flask on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
