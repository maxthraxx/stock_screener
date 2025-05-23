import os
import telegram
import asyncio
import re # Import re for escaping
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Basic validation
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID environment variable not set.")

# Initialize the bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def escape_markdown(text: str) -> str:
    """
    Escapes special characters for Telegram Markdown (basic version).

    Handles characters like _, *, `, and [
    Note: This is for the 'Markdown' parse mode, not 'MarkdownV2'.
    """
    if not isinstance(text, str):
        return ""
    # Only escape specific characters required for basic Markdown
    escape_chars = r'([_*`\[])' # Escape _, *, `, and [
    return re.sub(escape_chars, r'\\\1', text)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def send_telegram_message(message: str):
    """
    Sends a message to the specified Telegram chat ID.
    Retries up to 3 times with a 2-second delay if sending fails.

    Args:
        message: The text message to send (should be pre-escaped if needed).
    """
    if not message or not isinstance(message, str):
        print("Error: Invalid message content.")
        return

    try:
        print(f"Attempting to send message to chat ID {TELEGRAM_CHAT_ID}...")
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        print("Message sent successfully.")
    except telegram.error.TelegramError as e:
        print(f"Error sending Telegram message: {e}")
        raise # Reraise the exception to trigger tenacity retry

# Example usage (for testing purposes)
async def main():
    test_msg = "Hello from the Stock Screener!\n\n*This* is a test message with _special_ chars like [link](url) and `code` and - . !"
    escaped_msg = escape_markdown(test_msg)
    print(f"Original: {test_msg}")
    print(f"Escaped: {escaped_msg}")
    await send_telegram_message(escaped_msg)

if __name__ == "__main__":
    # Ensure you have an event loop running if calling from a script
    # If you run this file directly, it will use asyncio.run()
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Handle cases where an event loop is already running (e.g., in Jupyter)
        if "cannot run nest" in str(e):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise 