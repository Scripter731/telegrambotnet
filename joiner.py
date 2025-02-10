import random
import asyncio
import os
import logging
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon import events, types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSIONS_PATH = "sessions/"

class JoinerFunc:

    def __init__(self, api_id: int, api_hash: str):

        self.api_id = api_id
        self.api_hash = api_hash

    async def join(self, session: TelegramClient, link: str, mode: str):

        try:
            if mode == "1":
                if "joinchat" in link:
                    invite = link.split("/")[-1]
                    await session(ImportChatInviteRequest(invite))
                else:
                    await session(JoinChannelRequest(link))
                return True
            elif mode == "2":
                channel = await session(GetFullChannelRequest(link))
                chat = channel.chats[1]
                await session(JoinChannelRequest(chat))
                return True
        except Exception as error:
            logger.error(f"Ошибка при вступлении: {error}")
            return False

    async def solve_captcha(self, session: TelegramClient):

        session.add_event_handler(
            self.on_message,
            events.NewMessage
        )

        await session.run_until_disconnected()

    async def on_message(self, msg: types.Message):

        if msg.mentioned:
            if msg.reply_markup:
                captcha = msg.reply_markup.rows[0].buttons[0].data.decode("utf-8")
                await msg.click(data=captcha)

    async def execute(self, link: str, mode: str, speed: str, flood: bool, delay: int = 0):

        if not os.path.exists(SESSIONS_PATH):
            logger.error(f"Папка {SESSIONS_PATH} не существует.")
            return

        session_files = [f for f in os.listdir(SESSIONS_PATH) if f.endswith(".session")]
        if not session_files:
            logger.error(f"В папке {SESSIONS_PATH} нет файлов сессий.")
            return

        sessions = []
        for session_file in session_files:
            client = TelegramClient(
                session=os.path.join(SESSIONS_PATH, session_file),
                api_id=self.api_id,
                api_hash=self.api_hash
            )
            sessions.append(client)

        joined = 0
        start = asyncio.get_event_loop().time()

        if speed == "normal":
            for index, session in enumerate(sessions):
                await session.start()

                if flood:
                    asyncio.create_task(self.solve_captcha(session))

                is_joined = await self.join(session, link, mode)
                if is_joined:
                    joined += 1

                await asyncio.sleep(delay)
        elif speed == "fast":
            tasks = [self.join(session, link, mode) for session in sessions]
            results = await asyncio.gather(*tasks)
            joined = sum(1 for result in results if result)

        joined_time = round(asyncio.get_event_loop().time() - start, 2)
        logger.info(f"[+] {joined} ботов вступили за [yellow]{joined_time}[/]s")

        if flood:
            logger.info("[bold yellow]Флуд начат[/]")