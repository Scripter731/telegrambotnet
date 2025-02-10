import asyncio
import random
import os
import logging
from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSIONS_PATH = "sessions/"

class ReactionsFunc:

    def __init__(self, api_id: int, api_hash: str):

        self.api_id = api_id
        self.api_hash = api_hash
        self.reactions = ['👍', '❤️', '🔥', '🥰', '👏', '😁', '🎉', '🤩', '👎', '🤯', '😱', '🤬', '😢', '🤮', '💩', '🙏']

    async def set_reaction(self, session: TelegramClient, chat_username: str, message_id: int, reaction=None):

        if not reaction:
            reaction = random.choice(self.reactions)

        try:
            entity = await session.get_entity(chat_username)
            await session(SendReactionRequest(
                peer=entity,
                msg_id=int(message_id),
                reaction=[ReactionEmoji(emoticon=reaction)]
            ))
            logger.info(f"[SUCCESS] [{session.me.id}] : Reaction \"{reaction}\" was sent")
        except Exception as err:
            logger.error(f"[ERROR] [{session.me.id}] : {err}")

    async def execute(self, link_to_message: str, reaction: str = None):

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

        chat_username, message_id = link_to_message.split("/")[-2:]

        await asyncio.gather(*[
            self.set_reaction(
                session=session,
                chat_username=chat_username,
                message_id=message_id,
                reaction=reaction
            )
            for session in sessions
        ])