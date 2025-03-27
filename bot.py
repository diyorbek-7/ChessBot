import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Try to import analyze_game from chess_analyzer
try:
    from chess_analyzer import analyze_game
except ImportError as e:
    logging.error(f"Failed to import analyze_game from chess_analyzer: {str(e)}")
    analyze_game = None  # Set to None if import fails

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define your bot handlers
async def start(update, context):
    logger.info("Received /start command")
    await update.message.reply_text("Welcome! Send your chess game URL to make it reviewable.")

async def handle_message(update, context):
    message_text = update.message.text
    logger.info(f"Received message: {message_text}")
    await update.message.reply_text("Received your message. Processing...")

    try:
        # Check if analyze_game is available
        if analyze_game is None:
            raise ImportError("analyze_game function is not available. Check chess_analyzer.py.")

        # Check if the message contains a Chess.com URL
        if "chess.com" in message_text.lower():
            logger.info(f"Processing Chess.com URL: {message_text}")
            # Call the analyze_game function from chess_analyzer.py
            review_url = analyze_game(message_text)
            logger.info(f"Review URL generated: {review_url}")
            await update.message.reply_text(f"Game is reviewable! Review URL: {review_url}")
        else:
            logger.info("Message does not contain a Chess.com URL")
            await update.message.reply_text("Please send a valid Chess.com game URL.")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        await update.message.reply_text(f"Error processing your game: {str(e)}")

# Define a simple HTTP server for Render's Web Service requirement
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

def run_http_server():
    port = int(os.getenv("PORT", 8000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, DummyHandler)
    logger.info(f"Starting HTTP server on port {port}")
    httpd.serve_forever()

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN not set in environment variables")
        return

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()