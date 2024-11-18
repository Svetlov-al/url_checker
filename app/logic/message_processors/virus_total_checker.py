import asyncio
import base64
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


class VirusTotalChecker(AbstractMessageChecker):
    def __init__(
            self,
            api_key_repo: AbstractAPIKeyRepository,
            broker: BaseBroker,
            api_keys_entity: list[APIKeyEntity],
            queue: str = "virus_total",
            max_concurrent_requests: int = 10,

    ) -> None:
        self.semaphore: Semaphore = Semaphore(max_concurrent_requests)
        self.api_key_repo: AbstractAPIKeyRepository = api_key_repo
        self.broker: BaseBroker = broker
        self.api_keys: list[APIKeyEntity] = api_keys_entity
        self.queue: str = queue

    async def process_batch(self) -> dict[int, ResultStatus]:
        """Обрабатывает ссылки для всех ключей."""
        results = {}

        # => Создаём задачи для каждого ключа
        tasks = [self._process_key(key, results) for key in self.api_keys]

        await asyncio.gather(*tasks)

        logger.info(
            "Обработка сообщений завершена.\n"
            f"Количество обработанных ссылок: {len(results)}",
        )
        return results

    async def _process_key(self, key: APIKeyEntity, results: dict[str, ResultStatus]) -> None:
        """Обрабатывает все ссылки, связанные с данным ключом."""
        logger.info(f"Начинаем обработку ключа {key.key_id} с {len(key.links_to_process)} ссылками.")
        remaining_links: list[bytes] = []

        for link_data in key.links_to_process:
            for link_id, link_url in link_data.items():
                if not key.is_valid:
                    remaining_links.append(orjson.dumps({link_id: link_url}))
                    continue

                await self._process_link(link_id, link_url, key, results)

        if remaining_links:
            await self._publish_batch_in_queue(remaining_links=remaining_links)

    async def _process_link(
            self,
            link_id: str,
            link: str,
            key: APIKeyEntity,
            results: dict[str, str],
    ) -> None:
        async with self.semaphore:
            headers_generator = Headers(
                browser="chrome",
                os="win",
                headers=True,
            )
            headers = headers_generator.generate()
            headers["x-apikey"] = key.api_key
            proxy_url = key.get_proxy_url()

            try:
                encoded_url = base64.urlsafe_b64encode(link.encode()).decode().rstrip("=")
                async with httpx.AsyncClient(
                        proxies={"http": proxy_url, "https": proxy_url} if proxy_url else None,
                ) as client:
                    response = await client.get(
                        f'https://www.virustotal.com/api/v3/urls/{encoded_url}',
                        headers=headers,
                    )
                    if response.status_code == httpx.codes.OK:
                        data = response.json()
                        is_malicious = data['data']['attributes']['last_analysis_stats']['malicious'] > 0
                        results[link_id] = ResultStatus.FAIL if is_malicious else ResultStatus.GOOD
                        await self.api_key_repo.update_key_usage(key_id=key.key_id)

                    elif response.status_code in [httpx.codes.UNAUTHORIZED, httpx.codes.FORBIDDEN]:
                        logger.warning(f"API ключ {key.api_key} заблокирован или недействителен.")
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
            else:
                if key.delay:
                    await asyncio.sleep(key.delay)

    async def _push_message_back_in_queue(self, link_id: str, link: str) -> None:
        await self.broker.publish_message(
            queue_name=self.queue,
            message=orjson.dumps({link_id: link}),
        )

    async def _publish_batch_in_queue(self, remaining_links: list[bytes]) -> None:
        """Отправляет оставшиеся необработанные ссылки в очередь."""
        await self.broker.publish_batch(self.queue, remaining_links)
