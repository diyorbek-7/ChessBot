import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define your bot handlers
async def start(update, context):
    await update.message.reply_text("Welcome! Send your chess game URL to make it reviewable.")

async def handle_message(update, context):
    # Add your message handling logic here (e.g., process Chess.com URLs)
    await update.message.reply_text("Received your message. Processing...")

# Define a simple HTTP server for Render's Web Service requirement
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    # Get the port from the environment variable (Render sets PORT for Web Services)
    port = int(os.getenv("PORT", 8000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, DummyHandler)
    logger.info(f"Starting HTTP server on port {port}")
    httpd.serve_forever()

def main():
    # Get the Telegram token from environment variables
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN not set in environment variables")
        return

    # Create the Application and pass it your bot's token
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the HTTP server in a separate thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Start the bot
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()