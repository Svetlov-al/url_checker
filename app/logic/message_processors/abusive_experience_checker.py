import asyncio
import json
import logging
from asyncio import Semaphore

import httpx
from app.logic.message_processors.base import IMessageProcessor


logger = logging.getLogger(__name__)


class AbusiveExperienceChecker(IMessageProcessor):
    def __init__(self, api_key: str, client_id: str, max_concurrent_requests: int = 10):
        self.semaphore: Semaphore = Semaphore(max_concurrent_requests)
        self.api_key: str = api_key
        self.client_id: str = client_id

    async def process_batch(
        self,
        messages: list[bytes],
    ) -> dict[str, bool]:
        results = {}

        async with httpx.AsyncClient() as client:
            tasks = []
            for m in messages:
                tasks.append(self._process_message(client, m, results))
            await asyncio.gather(*tasks)

        return results

    async def _process_message(self, client: httpx.AsyncClient, message: bytes, results: dict[str, bool | None]):
        async with self.semaphore:
            try:
                message_data = json.loads(message)
                for Id, link in message_data.items():
                    response = await client.post(
                        'https://safebrowsing.googleapis.com/v4/threatMatches:find',
                        headers={
                            "Content-Type": "application/json",
                        },
                        json={
                            "client": {
                                "clientId": self.client_id,
                                "clientVersion": "1.5.2",
                            },
                            "threatInfo": {
                                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                                "platformTypes": ["ANY_PLATFORM"],
                                "threatEntryTypes": ["URL"],
                                "threatEntries": [
                                    {"url": link},
                                ],
                            },
                        },
                        params={
                            "key": self.api_key,
                        },
                    )
                    if response.status_code == 200:
                        data = response.json()
                        is_abusive = "matches" in data and len(data["matches"]) > 0
                        results[str(Id)] = is_abusive
                    else:
                        results[str(Id)] = None
            except json.JSONDecodeError:
                logger.error(
                    f"[AbusiveExperience]: Ошибка декодирования сообщения:\n"
                    f"Сообщение: {message}",
                )
            except Exception as e:
                logger.error(
                    f"[AbusiveExperience]: Неизвестная ошибка обработки сообщения:\n"
                    f"Error: {e}",
                )
