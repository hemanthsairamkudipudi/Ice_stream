import json

from confluent_kafka import Consumer, KafkaException

from kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
)


CONSUMER_GROUP_ID = "icestream-checkout-consumer"


def main() -> None:
    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": CONSUMER_GROUP_ID,
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe([KAFKA_TOPIC])

    print("=" * 60)
    print("IceStream Kafka Consumer")
    print("=" * 60)
    print(f"Kafka server : {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Kafka topic  : {KAFKA_TOPIC}")
    print(f"Consumer group: {CONSUMER_GROUP_ID}")
    print("=" * 60)
    print("[CONSUMER] Waiting for messages...")
    print("Press Ctrl+C to stop.")
    print()

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                raise KafkaException(message.error())

            key = (
                message.key().decode("utf-8")
                if message.key()
                else None
            )

            value = json.loads(
                message.value().decode("utf-8")
            )

            print(
                f"[RECEIVED] "
                f"partition={message.partition()} "
                f"offset={message.offset()} "
                f"key={key}"
            )

            print(
                json.dumps(
                    value,
                    indent=2,
                )
            )

            print("-" * 60)

    except KeyboardInterrupt:
        print("\n[CONSUMER] Stopping...")

    finally:
        consumer.close()
        print("[CONSUMER] Closed")


if __name__ == "__main__":
    main()