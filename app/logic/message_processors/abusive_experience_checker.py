import asyncio
import logging

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
    ) -> None:
        self.broker: BaseBroker = broker
        self.api_key_repo: AbstractAPIKeyRepository = api_key_repo
        self.api_keys: list[APIKeyEntity] = api_keys_entity
        self.queue: str = queue

    async def process_batch(self) -> dict[str, ResultStatus]:
        """Обрабатывает все ссылки для всех ключей."""
        results = {}

        logger.info(f"Начинаем обработку ссылок для {len(self.api_keys)} ключей.")

        tasks = [self._process_key(key, results) for key in self.api_keys]

        await asyncio.gather(*tasks)

        logger.info(
            "Обработка завершена.\n"
            f"Количество обработанных ссылок: {len(results)}.",
        )
        return results

    async def _process_key(self, key: APIKeyEntity, results: dict[str, ResultStatus]) -> None:
        """Обрабатывает все ссылки, связанные с данным ключом."""
        logger.info(f"Начинаем обработку ключа {key.key_id} с {len(key.links_to_process)} ссылками.")
        remaining_links: list[bytes] = []
        tasks = []

        for link_data in key.links_to_process:
            for link_id, link_url in link_data.items():
                if not key.is_valid:
                    logger.warning(f"Ключ {key.key_id} недействителен. Ссылка {link_id} пропущена.")
                    remaining_links.append(orjson.dumps({link_id: link_url}))
                    continue

                tasks.append(self._process_link(link_id, link_url, key, results))

        if tasks:
            await asyncio.gather(*tasks)

        if remaining_links:
            await self._publish_batch_in_queue(remaining_links)

    async def _process_link(
            self,
            link_id: str,
            link: str,
            key: APIKeyEntity,
            results: dict[str, ResultStatus],
    ) -> None:
        """Обрабатывает одну ссылку с учетом ограничений на количество
        запросов."""

        async with key.semaphore:
            headers_generator = Headers(browser="chrome", os="win", headers=True)
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

                        await self.api_key_repo.update_key_usage(key_id=key.key_id)

                    elif response.status_code in [httpx.codes.UNAUTHORIZED, httpx.codes.FORBIDDEN]:
                        logger.warning(f"API ключ {key.api_key} заблокирован или недействителен.")
                        await self.api_key_repo.mark_as_invalid(key_id=key.key_id)
                        key.is_valid = False
                        await self.api_key_repo.mark_as_invalid(key_id=key.key_id)
                        await self._push_message_back_in_queue(link_id, link)

                    elif response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                        logger.warning(f"API ключ {key.api_key} превысил лимит запросов.")
                        await self._push_message_back_in_queue(link_id, link)
                    else:
                        results[link_id] = ResultStatus.WAITING
                        await self.api_key_repo.update_key_usage(key_id=key.key_id)
                        await self._push_message_back_in_queue(link_id, link)

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP ошибка при запросе: {e}")
                results[link_id] = ResultStatus.WAITING
                await self._push_message_back_in_queue(link_id, link)

    async def _push_message_back_in_queue(self, link_id: str, link: str) -> None:
        await self.broker.publish_message(
            queue_name=self.queue,
            message=orjson.dumps({link_id: link}),
        )

    async def _publish_batch_in_queue(self, remaining_links: list[bytes]) -> None:
        """Отправляет оставшиеся необработанные ссылки в очередь."""
        await self.broker.publish_batch(self.queue, remaining_links)
