import httpx
import logging

from config import settings

logger = logging.getLogger(__name__)


def contact_po(visitor_name: str, message: str, contact_info: str) -> dict:
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id

    if not token or not chat_id:
        logger.warning("Telegram not configured — contact message logged instead.")
        log_msg = f"[CONTACT] From: {visitor_name} ({contact_info})\nMessage: {message}"
        logger.info(log_msg)
        return {
            "status": "logged",
            "message": "Your message has been received. I'll make sure Vaungsophal gets it.",
        }

    text = (
        f"\U0001f4ac New portfolio contact\n"
        f"From: {visitor_name}\n"
        f"Contact: {contact_info}\n"
        f"Message: {message}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        resp.raise_for_status()
        logger.info(f"Telegram notification sent for {visitor_name}")
        return {
            "status": "sent",
            "message": "Your message has been sent to Vaungsophal. He'll get back to you soon.",
        }
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return {
            "status": "error",
            "message": "Your message was received but delivery failed. Please try again later.",
        }
