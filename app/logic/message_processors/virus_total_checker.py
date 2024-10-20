import asyncio
import base64
import json
import logging
from asyncio import Semaphore

import httpx
from app.adapters.repositories.api_keys_repository import AbstractAPIKeyRepository
from app.logic.message_processors.base import IMessageProcessor


logger = logging.getLogger(__name__)


class VirusTotalChecker(IMessageProcessor):
    def __init__(
        self,
        api_key_repo: AbstractAPIKeyRepository,
        max_concurrent_requests: int = 10,
    ) -> None:
        self.semaphore: Semaphore = Semaphore(max_concurrent_requests)
        self.api_key_repo: AbstractAPIKeyRepository = api_key_repo

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
        logger.info(
            "Обработка сообщений завершена.\n"
            f"Количество обработанных сообщений: {len(results)}",
        )
        return results

    async def _process_message(
        self, client: httpx.AsyncClient, message: bytes, results: dict[str, bool | None],
    ) -> None:
        async with self.semaphore:
            try:
                message_data = json.loads(message)
                for Id, link in message_data.items():
                    encoded_url = base64.urlsafe_b64encode(link.encode()).decode().rstrip("=")
                    # => Загрузка ключей с лимитами
                    keys_with_limits = await self.api_key_repo.load_keys_from_db()
                    available_keys = [key for key, limit in keys_with_limits.items() if limit > 0]

                    while available_keys:
                        api_key = available_keys.pop(0)
                        logger.info(f"Обработка сообщения c ID: {Id}, url: {link}")

                        # => Отправляем запрос к API "Virus Total"
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

                            # => Обновляем лимит для ключа
                            await self.api_key_repo.update_key_usage(api_key)
                            break
                        elif response.status_code in [401, 403]:
                            await self.api_key_repo.mark_as_invalid(api_key)
                            logger.warning(f"API ключ {api_key} был заблокирован или недействителен.")
                            # => Продолжаем цикл для следующего ключа
                            continue
                        elif response.status_code == 429:
                            logger.warning(f"API ключ {api_key} превысил лимит запросов.")
                            # => Пытаемся использовать следующий ключ
                            continue
                        else:
                            results[str(Id)] = None
                            # => Прерываем обработку для этого сообщения
                            break
                    if str(Id) not in results:
                        results[str(Id)] = None
                        logger.warning("Нет доступных ключей для обработки сообщения.")

            except json.JSONDecodeError:
                logger.error(f"[VirusTotal]: Ошибка декодирования сообщения:\nСообщение: {message}")
            except Exception as e:
                logger.error(f"[VirusTotal]: Неизвестная ошибка обработки сообщения:\nError: {e}")
