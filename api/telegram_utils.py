import logging
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(text: str) -> None:
    """Best-effort admin notification via the configured Telegram bot.

    Never raises — a failed notification must not itself become an error,
    especially when called from error-handling code (see api/exceptions.py).
    No-op if TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID aren't set.
    """
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': settings.TELEGRAM_CHAT_ID, 'text': text}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        logger.exception("Failed to send Telegram notification")
