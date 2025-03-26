# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from chess_analyzer import get_review_url
import config


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(TimedOut)
)
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None):
    """Send a message with retry capability."""
    return await update.message.reply_text(text, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await send_message(update, context, "Welcome! Send your chess game URL to make it reviewable.")


async def process_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages containing Chess.com game URLs."""
    url = update.message.text.strip()

    if not ("chess.com" in url.lower() and "game" in url.lower()):
        await send_message(update, context,
                           "Please provide a valid Chess.com game URL (e.g., https://www.chess.com/game/live/123456789)")
        return

    await send_message(update, context, "Analyzing your game... Please wait.")

    # Extract URL if message contains multiple words
    if " " in url:
        url = next((word for word in url.split() if "chess.com" in word.lower()), url)

    review_url = get_review_url(url)

    if review_url:
        keyboard = [[InlineKeyboardButton("View Game Review", url=review_url)]]
        await send_message(update, context, "Here's your game review:",
                           reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await send_message(update, context, "THE GAME IS REVIEWABLE!\nOpen it in the app or website, or simply click your link.")


def main():
    """Initialize and run the Telegram bot."""
    app = Application.builder() \
        .token(config.TELEGRAM_TOKEN) \
        .read_timeout(30) \
        .write_timeout(30) \
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_url))

    print("Bot started...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, timeout=120)


if __name__ == "__main__":
    main()