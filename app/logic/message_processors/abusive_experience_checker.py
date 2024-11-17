import asyncio
import json
import logging
from asyncio import Semaphore

import httpx
from app.adapters.orm.result import ResultStatus
from app.adapters.repositories.api_keys_repository import AbstractAPIKeyRepository
from app.domain.entities.api_key_entity import APIKeyEntity
from app.infra.broker.base import BaseBroker
from app.logic.message_processors.base import AbstractMessageChecker
from fake_headers import Headers
from orjson import orjson


logger = logging.getLogger(__name__)


class AbusiveExperienceChecker(AbstractMessageChecker):
    def __init__(
            self,
            api_key_repo: AbstractAPIKeyRepository,
            broker: BaseBroker,
            api_keys_entity: list[APIKeyEntity],
            queue: str = "abusive_exp",
            max_concurrent_requests: int = 10,
    ) -> None:
        self.semaphore: Semaphore = Semaphore(max_concurrent_requests)
        self.broker: BaseBroker = broker
        self.api_key_repo: AbstractAPIKeyRepository = api_key_repo
        self.api_key_locks = {key.api_key: asyncio.Lock() for key in api_keys_entity}
        self.api_keys: list[APIKeyEntity] = api_keys_entity
        self.queue: str = queue

    async def process_batch(
            self,
            messages: list[bytes],
    ) -> dict[str, bool]:
        results = {}

        tasks = []
        logger.info(
            "Обработка сообщений начата.\n"
            f"Количество сообщений в очереди: {len(messages)}",
        )
        for m in messages:
            tasks.append(self._process_message(m, results))

        await asyncio.gather(*tasks)

        logger.info(
            "Обработка сообщений завершена.\n"
            f"Количество обработанных сообщений: {len(results)}",
        )
        return results

    async def _process_message(
            self,
            message: bytes,
            results: dict[str, str],
    ) -> None:
        try:
            message_data = json.loads(message)
            for Id, link in message_data.items():
                await self._process_link(Id, link, results)
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")

    async def _process_link(
            self,
            link_id: str,
            link: str,
            results: dict[str, str],
    ) -> None:
        async with self.semaphore:
            for index, key in enumerate(self.api_keys):
                if not key.is_valid:
                    logger.warning(f"Ключ {key.api_key} заблокирован или недействителен.")
                    await self.check_last_key_and_push_message(index, link_id, link)
                    continue

                if key.limit <= 0:
                    logger.warning(f"Ключ {key.api_key} исчерпал лимит.")
                    await self.check_last_key_and_push_message(index, link_id, link)
                    continue

                lock = self.api_key_locks.get(key.api_key)

                if lock:
                    if lock.locked() and index == len(self.api_keys) - 1:
                        logger.warning(f"Ключ {key.key_id} последний и заблокирован, ждем завершения.")
                        await lock.acquire()

                    elif lock.locked() and index < len(self.api_keys) - 1:
                        logger.warning(f"Ключ не последний {key.key_id} и заблокирован, пробуем следующий.")
                        continue

                    await lock.acquire()

                    headers_generator = Headers(
                        browser="chrome",
                        os="win",
                        headers=True,
                    )

                    headers = headers_generator.generate()
                    proxy_url = key.get_proxy_url()

                    try:
                        async with httpx.AsyncClient(
                                proxies={"http": proxy_url, "https": proxy_url} if proxy_url else None,
                        ) as client:
                            # => Отправляем запрос к API "Abusive Experience Report"
                            response = await client.get(
                                f'https://abusiveexperiencereport.googleapis.com/v1/sites/{link}',
                                headers=headers,
                                params={"key": key.api_key},
                            )

                            if response.status_code == httpx.codes.OK:
                                data = response.json()

                                # => Проверяем статус сайта на наличие нарушений
                                abusive_status = data.get("abusiveStatus")

                                if abusive_status == "FAILING":
                                    # => Сайт признан нарушающим (FAILING)
                                    is_abusive = ResultStatus.FAIL
                                elif abusive_status == "WARNING":
                                    # => Сайт под предупреждением, но не нарушает
                                    is_abusive = ResultStatus.GOOD
                                elif abusive_status == "PASSING":
                                    is_abusive = ResultStatus.GOOD
                                else:
                                    is_abusive = ResultStatus.EMPTY

                                results[link_id] = is_abusive

                                key.used_limit += 1
                                await self.api_key_repo.update_key_usage(key_id=key.key_id)
                                if key.delay:
                                    await asyncio.sleep(key.delay)
                                break

                            elif response.status_code in [httpx.codes.UNAUTHORIZED, httpx.codes.FORBIDDEN]:
                                logger.warning(f"API ключ {key.api_key} заблокирован или недействителен.")
                                await self.api_key_repo.mark_as_invalid(key_id=key.key_id)
                                key.is_valid = False
                                await self.check_last_key_and_push_message(index, link_id, link)
                                continue

                            elif response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                                logger.warning(f"API ключ {key.api_key} превысил лимит запросов.")
                                await self.check_last_key_and_push_message(index, link_id, link)
                                await asyncio.sleep(15)
                                continue
                            else:
                                results[link_id] = ResultStatus.WAITING
                                key.used_limit += 1
                                await self.api_key_repo.update_key_usage(key_id=key.key_id)
                                await self.broker.publish_message(
                                    queue_name=self.queue,
                                    message=orjson.dumps({link_id: link}),
                                )
                    except httpx.HTTPStatusError as e:
                        logger.error(f"HTTP ошибка при запросе: {e}")
                        results[link_id] = ResultStatus.WAITING
                        await self.broker.publish_message(
                            queue_name=self.queue,
                            message=orjson.dumps({link_id: link}),
                        )
                    finally:
                        if lock:
                            lock.release()

    async def check_last_key_and_push_message(self, index: int, link_id: str, link: str) -> None:
        if index == len(self.api_keys) - 1:
            await self.broker.publish_message(
                queue_name=self.queue,
                message=orjson.dumps({link_id: link}),
            )
