import base64
import json
import logging
from dataclasses import dataclass

import httpx
from app.logic.message_processors.base import IMessageProcessor


logger = logging.getLogger(__name__)


@dataclass
class VirusTotalChecker(IMessageProcessor):

    async def process_batch(
        self,
        api_key: str,
        messages,
    ) -> dict[str, bool]:
        results = {}

        async with httpx.AsyncClient() as client:
            for m in messages:
                try:
                    message_data = json.loads(m.value)
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
                        f"Сообщение: {m.value}",
                    )
                except Exception as e:
                    logger.error(
                        f"[VirusTotal]: Неизвестная ошибка обработки сообщения:\n"
                        f"Error: {e}",
                    )

        return results
