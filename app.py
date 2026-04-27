from flask import Flask, request, jsonify
import asyncio
import logging
import threading
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

# Bot application instance
bot_app = None
bot_initialized = False
init_lock = threading.Lock()

def run_async(coro):
    """Run async function in new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def get_or_create_bot():
    """Get bot instance or create if not exists"""
    global bot_app, bot_initialized
    
    with init_lock:
        if bot_initialized:
            return bot_app
        
        logger.info("🚀 Initializing bot for first time...")
        
        # Create application
        bot_app = create_application()
        
        # Initialize in separate thread to avoid event loop conflicts
        run_async(bot_app.initialize())
        run_async(bot_app.start())
        
        # Set webhook
        webhook_url = os.getenv('WEBHOOK_URL', '')
        if webhook_url:
            try:
                run_async(bot_app.bot.set_webhook(url=webhook_url))
                logger.info(f"✅ Webhook set: {webhook_url}")
            except Exception as e:
                logger.error(f"❌ Webhook setup failed: {e}")
        else:
            logger.warning("⚠️ WEBHOOK_URL not set!")
        
        bot_initialized = True
        logger.info("✅ Bot initialized successfully!")
        
        return bot_app

@app.route('/')
def home():
    """Home endpoint"""
    return """
    <html>
    <head>
        <title>Thumbnail Generator Bot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                text-align: center;
                background: rgba(255,255,255,0.1);
                padding: 50px 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                max-width: 600px;
            }
            h1 { 
                font-size: 2.5em; 
                margin-bottom: 10px;
            }
            .status { 
                font-size: 1.3em; 
                margin: 20px 0;
                color: #4ade80;
                font-weight: 600;
            }
            .info {
                font-size: 1.1em;
                opacity: 0.95;
                line-height: 1.8;
            }
            .info p { margin: 10px 0; }
            @media (max-width: 600px) {
                h1 { font-size: 2em; }
                .container { padding: 30px 20px; }
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
    """Handle Telegram webhook"""
    try:
        # Get bot instance
        app_instance = get_or_create_bot()
        
        # Get update data
        update_data = request.get_json(force=True)
        logger.info(f"📥 Webhook received: {update_data.get('update_id', 'unknown')}")
        
        # Process update
        update = Update.de_json(update_data, app_instance.bot)
        run_async(app_instance.process_update(update))
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "bot": "ready" if bot_initialized else "not_initialized",
        "mode": "webhook"
    }), 200

@app.route('/setwebhook')
def set_webhook_route():
    """Manually set webhook"""
    try:
        webhook_url = os.getenv('WEBHOOK_URL', '')
        if not webhook_url:
            return jsonify({
                "status": "error",
                "message": "WEBHOOK_URL not set in environment variables"
            }), 400
        
        # Get or create bot
        app_instance = get_or_create_bot()
        
        # Set webhook
        run_async(app_instance.bot.set_webhook(url=webhook_url))
        
        # Get webhook info
        webhook_info = run_async(app_instance.bot.get_webhook_info())
        
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url,
            "current_webhook": webhook_info.url,
            "pending_update_count": webhook_info.pending_update_count
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Set webhook error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/deletewebhook')
def delete_webhook():
    """Delete webhook (for debugging)"""
    try:
        app_instance = get_or_create_bot()
        run_async(app_instance.bot.delete_webhook(drop_pending_updates=True))
        
        return jsonify({
            "status": "success",
            "message": "Webhook deleted"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7860))
    logger.info(f"🚀 Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
