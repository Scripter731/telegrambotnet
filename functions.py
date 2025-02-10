import asyncio
import logging
import os
from report import report_user
from reactions import ReactionsFunc
from joiner import join_chat
from config import API_ID, API_HASH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSIONS_PATH = "sessions/"

class FunctionManager:
    def __init__(self, sessions, api_id: int, api_hash: str):
        self.sessions = sessions
        self.api_id = api_id
        self.api_hash = api_hash

    async def execute(self, command: str, **kwargs):
        if command == "report":
            func = report_user
            args = (kwargs["username"], kwargs["reason_choice"], kwargs["comment"], self.api_id, self.api_hash)
        elif command == "reaction_flood":
            func = ReactionsFunc(self.sessions, self.api_id, self.api_hash).execute
            args = (kwargs["link"], kwargs.get("reaction"))
        elif command == "join":
            func = join_chat
            args = (kwargs["link"], kwargs["mode"], kwargs["speed"], kwargs.get("flood", False), kwargs.get("delay", 0), self.api_id, self.api_hash)
        else:
            raise ValueError("Неизвестная команда")

        for i in range(0, len(self.sessions), 3):
            group = self.sessions[i:i + 3]
            tasks = []

            for session in group:
                if command == "report":
                    tasks.append(func(*args, session))
                elif command == "reaction_flood":
                    tasks.append(func(*args))
                elif command == "join":
                    tasks.append(func(*args, session))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            successful = 0
            failed = 0
            for result in results:
                if isinstance(result, tuple):
                    successful += result[0]
                    failed += result[1]
                else:
                    logger.error(f"Ошибка при выполнении задачи: {result}")
                    failed += 1

            logger.info(f"Группа из {len(group)} сессий завершена. Успешно: {successful}, Неудачно: {failed}")

            delay = 10  
            logger.info(f"Ожидание {delay} секунд перед следующей группой...")
            await asyncio.sleep(delay)