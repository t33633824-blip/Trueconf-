"""
TrueConf ↔ Telegram Integration Bot
Мониторинг Telegram каналов с пересылкой в TrueConf по ключевым словам
"""

import asyncio
import logging
from telethon import TelegramClient, events
from config.settings import (
    API_ID, API_HASH, CHANNELS, SESSION_NAME
)
from config.keywords import KEYWORD_RULES
from trueconf_client import TrueConfClient
from logger import setup_logger

logger = setup_logger()
tc = TrueConfClient()


@events.register(events.NewMessage(chats=CHANNELS))
async def handle_message(event):
    text = event.message.text or ""
    if not text:
        return

    try:
        channel = getattr(event.chat, "username", None) or event.chat.title
    except Exception:
        channel = "unknown"

    for rule in KEYWORD_RULES:
        matched = [kw for kw in rule["keywords"] if kw.lower() in text.lower()]
        if matched:
            keywords_str = ", ".join(matched)
            msg = (
                f"🔔 Канал: @{channel}\n"
                f"🏷 Ключевые слова: {keywords_str}\n"
                f"📝 {text[:500]}"
            )
            success = tc.send_message(rule["conference_id"], msg)
            if success:
                logger.info(f"[OK] @{channel} → конф. {rule['conference_id']} | слова: {keywords_str}")
            else:
                logger.error(f"[FAIL] Не удалось отправить в TrueConf конф. {rule['conference_id']}")


async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    client.add_event_handler(handle_message)
    await client.start()
    logger.info("✅ Бот запущен. Мониторинг каналов: %s", CHANNELS)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
