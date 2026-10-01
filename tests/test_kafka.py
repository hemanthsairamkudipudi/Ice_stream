import json

from generator.checkout_generator import CheckoutGenerator
from kafka.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC


def test_kafka_bootstrap_server_configuration():
    assert KAFKA_BOOTSTRAP_SERVERS == "localhost:9092"


def test_kafka_topic_configuration():
    assert KAFKA_TOPIC == "checkout-topic"


def test_event_can_be_serialized_to_json():
    generator = CheckoutGenerator()
    event = generator.generate_event()

    serialized = json.dumps(event)

    assert isinstance(serialized, str)
    assert event["order_id"] in serialized


def test_event_can_be_deserialized_from_json():
    generator = CheckoutGenerator()
    event = generator.generate_event()

    serialized = json.dumps(event)
    deserialized = json.loads(serialized)

    assert deserialized == event


def test_event_contains_kafka_message_key():
    generator = CheckoutGenerator()
    event = generator.generate_event()

    message_key = event["order_id"]

    assert isinstance(message_key, str)
    assert message_key.startswith("ORD")


def test_event_preserves_anomaly_fields():
    event = {
        "order_id": "ORDTEST001",
        "customer_id": "CUS001",
        "product_id": "P101",
        "amount": 1000.0,
        "tax_amount": None,
        "payment_status": "SUCCESS",
        "timestamp": "2026-09-30T00:00:00+00:00",
        "unexpected_field": "SCHEMA_DRIFT",
    }

    serialized = json.dumps(event)
    deserialized = json.loads(serialized)

    assert deserialized["tax_amount"] is None
    assert deserialized["unexpected_field"] == "SCHEMA_DRIFT"
    