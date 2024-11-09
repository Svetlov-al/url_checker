import asyncio
import json
import logging
from asyncio import Semaphore

import httpx
from app.adapters.repositories.api_keys_repository import AbstractAPIKeyRepository
from app.logic.message_processors.base import AbstractMessageChecker


logger = logging.getLogger(__name__)


class AbusiveExperienceChecker(AbstractMessageChecker):
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
        proxy: str | None = None,
    ) -> dict[str, bool]:
        results = {}

        async with httpx.AsyncClient(proxy=proxy) as client:
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
                    # => Загрузка ключей с лимитами
                    keys_with_limits = await self.api_key_repo.load_keys_from_db()
                    available_keys = [key for key, limit in keys_with_limits.items() if limit > 0]

                    while available_keys:
                        api_key = available_keys.pop(0)
                        logger.info(f"Обработка сообщения с ID: {Id}, url: {link}")

                        # => Отправляем запрос к API "Abusive Experience Report"
                        response = await client.get(
                            f'https://abusiveexperiencereport.googleapis.com/v1/sites/{link}',
                            params={"key": api_key},
                        )

                        if response.status_code == 200:
                            data = response.json()
                            # => Проверяем статус сайта на наличие нарушений
                            abusive_status = data.get("abusiveStatus")

                            if abusive_status == "FAILING":
                                # => Сайт признан нарушающим (FAILING)
                                is_abusive = True
                            elif abusive_status == "WARNING":
                                # => Сайт под предупреждением, но не нарушает
                                is_abusive = False
                            elif abusive_status == "PASSING":
                                is_abusive = False
                            else:
                                is_abusive = None
                            results[str(Id)] = is_abusive

                            # => Обновляем лимит для ключа
                            await self.api_key_repo.update_key_usage(api_key)
                            break
                        elif response.status_code in [401, 403]:
                            await self.api_key_repo.mark_as_invalid(api_key)
                            logger.warning(f"API ключ {api_key} был заблокирован или недействителен.")
                            continue
                        elif response.status_code == 429:
                            logger.warning(f"API ключ {api_key} превысил лимит запросов.")
                            continue
                        else:
                            results[str(Id)] = None
                            logger.error(f"Ошибка запроса для сайта {link}: {response.status_code}")
                            break

                    if str(Id) not in results:
                        results[str(Id)] = None
                        logger.warning(f"Нет доступных ключей для обработки сообщения с ID {Id}.")

            except json.JSONDecodeError:
                logger.error(f"[AbusiveExperience]: Ошибка декодирования сообщения:\nСообщение: {message}")
            except Exception as e:
                logger.error(f"[AbusiveExperience]: Неизвестная ошибка обработки сообщения:\nError: {e}")
