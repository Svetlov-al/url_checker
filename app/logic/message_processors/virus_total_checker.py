import asyncio
import base64
import json
import logging
from asyncio import Semaphore

import httpx
from app.logic.message_processors.base import IMessageProcessor


logger = logging.getLogger(__name__)


class VirusTotalChecker(IMessageProcessor):
    def __init__(self, max_concurrent_requests: int = 5):
        self.semaphore = Semaphore(max_concurrent_requests)

    async def process_batch(
        self,
        api_key: str,
        messages: dict[str, str],
    ) -> dict[str, bool]:
        results = {}

        async with httpx.AsyncClient() as client:
            tasks = []
            for m in messages:
                tasks.append(self._process_message(client, api_key, m, results))
            await asyncio.gather(*tasks)

        return results

    async def _process_message(self, client, api_key: str, message, results: dict):
        async with self.semaphore:
            try:
                message_data = json.loads(message)
                for Id, link in message_data.items():
                    encoded_url = base64.urlsafe_b64encode(link.encode()).decode().rstrip("=")
                    response = await client.get(
                        f'https://www.virustotal.com/api/v3/urls/{encoded_url}',
                        headers={
                            "accept": "application/json",
                            "x-apikey": api_key,
                        },
                    )
                    if response.status_code == 200:
                        data = response.json()
                        is_malicious = data['data']['attributes']['last_analysis_stats']['malicious'] > 0
                        results[str(Id)] = is_malicious
                    else:
                        results[str(Id)] = None
            except json.JSONDecodeError:
                logger.error(
                    f"[VirusTotal]: Ошибка декодирования сообщения:\n"
                    f"Сообщение: {message}",
                )
            except Exception as e:
                logger.error(
                    f"[VirusTotal]: Неизвестная ошибка обработки сообщения:\n"
                    f"Error: {e}",
                )
