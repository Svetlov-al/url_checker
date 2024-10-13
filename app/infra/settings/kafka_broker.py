from aiokafka import (
    AIOKafkaConsumer,
    AIOKafkaProducer,
)

from infra.broker.kafka_consumer import KafkaMessageConsumer
from infra.broker.kafka_producer import KafkaMessageProducer


def create_message_producer(kafka_url: str) -> KafkaMessageProducer:
    return KafkaMessageProducer(
        AIOKafkaProducer(bootstrap_servers=kafka_url),
    )


def create_message_consumer(kafka_url: str) -> KafkaMessageConsumer:
    return KafkaMessageConsumer(
        AIOKafkaConsumer(
            "links",
            bootstrap_servers=kafka_url,
            group_id="links_group",
            metadata_max_age_ms=30000,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        ),
    )
