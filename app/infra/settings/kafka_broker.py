from aiokafka import (
    AIOKafkaConsumer,
    AIOKafkaProducer,
)

from infra.broker.base import BaseMessageBroker
from infra.broker.kafka import KafkaMessageBroker


def create_message_broker(kafka_url: str) -> BaseMessageBroker:
    return KafkaMessageBroker(
        producer=AIOKafkaProducer(bootstrap_servers=kafka_url),
        consumer=AIOKafkaConsumer(
            bootstrap_servers=kafka_url,
            group_id="links_group",
            metadata_max_age_ms=30000,
        ),
    )
