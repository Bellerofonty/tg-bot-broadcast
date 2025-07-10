import asyncio
import csv
from io import StringIO
from telegram import Bot
from telegram.error import TelegramError
from aiohttp import ClientError
from socket import timeout
from telegram.request import HTTPXRequest

BATCH_SIZE = 20
DELAY_BETWEEN_MESSAGES = 1
DELAY_BETWEEN_BATCHES = 10

async def _send_messages(bot_token, user_ids, message):
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    bot = Bot(token=bot_token, request=request)

    failed_to_send = {}

    for i in range(0, len(user_ids), BATCH_SIZE):
        batch = user_ids[i:i + BATCH_SIZE]

        for user_id in batch:
            try:
                await bot.send_message(chat_id=user_id, text=message)
            except (TelegramError, ClientError, timeout, asyncio.TimeoutError) as e:
                failed_to_send[user_id] = str(e)
            await asyncio.sleep(DELAY_BETWEEN_MESSAGES)

        await asyncio.sleep(DELAY_BETWEEN_BATCHES)

    return failed_to_send

def send_messages(bot_token: str, user_ids: list[str], message: str):
    failed = asyncio.run(_send_messages(bot_token, user_ids, message))

    success_count = len(user_ids) - len(failed)
    total_count = len(user_ids)
    summary = f"{success_count}/{total_count} messages sent successfully."

    if not failed:
        return summary, None

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['user_id', 'error_message'])
    for uid, err in failed.items():
        writer.writerow([uid, err])

    return summary, output.getvalue()
