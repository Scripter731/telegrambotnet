from telethon import TelegramClient
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonSpam, InputReportReasonChildAbuse, InputReportReasonCopyright, InputReportReasonFake, InputReportReasonPornography, InputReportReasonViolence, InputReportReasonOther
import os
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSIONS_PATH = "sessions/"

REASON_MAPPING = {
    1: InputReportReasonChildAbuse(),
    2: InputReportReasonCopyright(),
    3: InputReportReasonFake(),
    4: InputReportReasonPornography(),
    5: InputReportReasonSpam(),
    6: InputReportReasonViolence(),
    7: InputReportReasonOther()
}

async def report_user(username: str, reason_choice: int, comment: str, api_id: int, api_hash: str) -> (int, int):

    successful_reports = 0
    failed_reports = 0

    if not os.path.exists(SESSIONS_PATH):
        logger.error(f"Папка {SESSIONS_PATH} не существует.")
        return successful_reports, failed_reports

    session_files = [f for f in os.listdir(SESSIONS_PATH) if f.endswith(".session")]
    if not session_files:
        logger.error(f"В папке {SESSIONS_PATH} нет файлов сессий.")
        return successful_reports, failed_reports

    for session_file in session_files:
        client: TelegramClient = TelegramClient(
            session=os.path.join(SESSIONS_PATH, session_file),
            api_id=api_id,
            api_hash=api_hash
        )
        await client.connect()

        if not client.is_user_authorized:
            logger.error(f"Сессия {session_file} не авторизована.")
            failed_reports += 1
            continue

        try:
            entity = await client.get_entity(username)
            reason = REASON_MAPPING.get(reason_choice, InputReportReasonSpam())
            await client(ReportRequest(
                peer=entity,
                id=[entity.id],
                reason=reason,
                message=comment
            ))
            logger.info(f"Жалоба на {username} отправлена.")
            successful_reports += 1
        except Exception as e:
            logger.error(f"Ошибка при отправке жалобы: {e}")
            failed_reports += 1
        finally:
            await client.disconnect()

    return successful_reports, failed_reports