import asyncio
import logging
import os
from telethon import TelegramClient
from telethon.network import ConnectionTcpMTProxyRandomizedIntermediate
from config import load_config, API_ID, API_HASH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSIONS_PATH = "sessions/"

async def load_sessions():

    sessions = []
    if not os.path.exists(SESSIONS_PATH):
        logger.error(f"Папка {SESSIONS_PATH} не существует.")
        return sessions

    session_files = [f for f in os.listdir(SESSIONS_PATH) if f.endswith(".session")]
    if not session_files:
        logger.error(f"В папке {SESSIONS_PATH} нет файлов сессий.")
        return sessions

    for session_file in session_files:
        client = TelegramClient(
            session=os.path.join(SESSIONS_PATH, session_file),
            api_id=API_ID,
            api_hash=API_HASH
        )
        sessions.append(client)

    return sessions

async def initialize_sessions(sessions, proxies=None):

    if not sessions:
        logger.info("Нет активных сессий.")
        return

    for i in range(0, len(sessions), 3):
        group = sessions[i:i + 3]
        proxy = random.choice(proxies) if proxies else None

        tasks = []
        for session in group:
            if proxy:
                session.set_proxy(proxy)
            tasks.append(session.start())

        await asyncio.gather(*tasks)
        logger.info(f"Инициализировано {len(group)} сессий.")