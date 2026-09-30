import json
import random
import time
from datetime import datetime, timezone
from typing import Any

from generator.config import (
    CONTINUOUS_MODE,
    DUPLICATE_RATE,
    EVENTS_PER_SECOND,
    INVALID_VALUE_RATE,
    NULL_TAX_RATE,
    SCHEMA_DRIFT_RATE,
    TOTAL_EVENTS,
    validate_config,
)


PRODUCT_IDS = [
    "P101",
    "P102",
    "P103",
    "P104",
    "P105",
]

PAYMENT_STATUSES = [
    "SUCCESS",
    "SUCCESS",
    "SUCCESS",
    "FAILED",
]


class CheckoutGenerator:
    """Generate realistic e-commerce checkout telemetry."""

    def __init__(self) -> None:
        self.order_number = 100000
        self.last_event: dict[str, Any] | None = None

    def _next_order_id(self) -> str:
        self.order_number += 1
        return f"ORD{self.order_number}"

    def _generate_normal_event(self) -> dict[str, Any]:
        amount = round(random.uniform(100.0, 10000.0), 2)

        tax_rate = 0.18
        tax_amount = round(amount * tax_rate, 2)

        event = {
            "order_id": self._next_order_id(),
            "customer_id": f"CUS{random.randint(100, 999):03d}",
            "product_id": random.choice(PRODUCT_IDS),
            "amount": amount,
            "tax_amount": tax_amount,
            "payment_status": random.choice(PAYMENT_STATUSES),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return event

    def _inject_anomalies(self, event: dict[str, Any]) -> dict[str, Any]:
        anomaly_injected = False

        # NULL tax_amount
        if random.random() < NULL_TAX_RATE:
            event["tax_amount"] = None
            print(
                f"[ANOMALY] Injected NULL tax_amount "
                f"into {event['order_id']}"
            )
            anomaly_injected = True

        # Negative amount
        if random.random() < INVALID_VALUE_RATE:
            event["amount"] = -abs(event["amount"])
            print(
                f"[ANOMALY] Injected negative amount "
                f"into {event['order_id']}"
            )
            anomaly_injected = True

        # Schema drift
        if random.random() < SCHEMA_DRIFT_RATE:
            event["unexpected_field"] = "SCHEMA_DRIFT"
            print(
                f"[ANOMALY] Injected schema drift "
                f"into {event['order_id']}"
            )
            anomaly_injected = True

        # Duplicate event
        if (
            self.last_event is not None
            and random.random() < DUPLICATE_RATE
        ):
            print(
                f"[ANOMALY] Generated duplicate event "
                f"for {self.last_event['order_id']}"
            )
            return self.last_event.copy()

        if not anomaly_injected:
            print(f"[STREAM] Generated order {event['order_id']}")

        return event

    def generate_event(self) -> dict[str, Any]:
        event = self._generate_normal_event()
        event = self._inject_anomalies(event)

        self.last_event = event.copy()

        return event

    def run(self) -> None:
        validate_config()

        print("=" * 60)
        print("IceStream Checkout Event Generator")
        print("=" * 60)

        print(f"Events per second : {EVENTS_PER_SECOND}")
        print(f"Total events      : {TOTAL_EVENTS}")
        print(f"Continuous mode   : {CONTINUOUS_MODE}")
        print(f"NULL tax rate     : {NULL_TAX_RATE * 100:.2f}%")
        print(f"Schema drift rate : {SCHEMA_DRIFT_RATE * 100:.2f}%")
        print(f"Duplicate rate    : {DUPLICATE_RATE * 100:.2f}%")
        print(f"Invalid rate      : {INVALID_VALUE_RATE * 100:.2f}%")
        print("=" * 60)

        delay = 1 / EVENTS_PER_SECOND

        generated = 0

        while CONTINUOUS_MODE or generated < TOTAL_EVENTS:
            event = self.generate_event()

            print(
                "[EVENT]",
                json.dumps(event, separators=(",", ":"))
            )

            generated += 1

            if not CONTINUOUS_MODE and generated >= TOTAL_EVENTS:
                break

            time.sleep(delay)

        print("=" * 60)
        print(f"[DONE] Generated {generated} events")
        print("=" * 60)


if __name__ == "__main__":
    generator = CheckoutGenerator()
    generator.run()