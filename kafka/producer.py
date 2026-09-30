import json

from confluent_kafka import Producer

from generator.checkout_generator import CheckoutGenerator
from kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
)


def delivery_report(error, message) -> None:
    """
    Called by Kafka after a message has been delivered
    or delivery has failed.
    """

    if error is not None:
        print(
            f"[KAFKA ERROR] "
            f"Delivery failed: {error}"
        )
        return

    key = (
        message.key().decode("utf-8")
        if message.key()
        else None
    )

    print(
        f"[KAFKA] Delivered "
        f"key={key} "
        f"partition={message.partition()} "
        f"offset={message.offset()}"
    )


def main() -> None:
    producer = Producer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        }
    )

    generator = CheckoutGenerator()

    number_of_events = 20

    print("=" * 60)
    print("IceStream Kafka Producer")
    print("=" * 60)
    print(
        f"Kafka server : {KAFKA_BOOTSTRAP_SERVERS}"
    )
    print(
        f"Kafka topic  : {KAFKA_TOPIC}"
    )
    print(
        f"Events       : {number_of_events}"
    )
    print("=" * 60)

    for _ in range(number_of_events):

        event = generator.generate_event()

        order_id = event["order_id"]

        producer.produce(
            topic=KAFKA_TOPIC,
            key=order_id.encode("utf-8"),
            value=json.dumps(event).encode("utf-8"),
            callback=delivery_report,
        )

        # Process delivery callbacks.
        producer.poll(0)

    # Wait for all queued messages to be delivered.
    remaining = producer.flush()

    if remaining > 0:
        print(
            f"[WARNING] {remaining} "
            f"message(s) were not delivered."
        )
    else:
        print(
            "[KAFKA] All messages delivered successfully."
        )

    print("=" * 60)
    print("[DONE] Producer finished")
    print("=" * 60)


if __name__ == "__main__":
    main()