import logging
from telegram import Bot

from utils.db import get_code

async def send_telegram_alert(message):
    try:
        telegram_token = get_code("TELEGRAM_TOKEN")
        telegram_chat_id = get_code("TELEGRAM_CHAT_ID")
        bot = Bot(token=telegram_token)
        await bot.send_message(chat_id=telegram_chat_id, text=message)
    except Exception as e:
        logging.error(f"텔레그램 전송 오류: {e}")