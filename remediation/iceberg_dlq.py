from datetime import datetime, timezone
from typing import Any

import pyarrow as pa
from pyiceberg.catalog import load_catalog


class IcebergDLQ:
    def __init__(
        self,
        catalog_uri: str = "http://localhost:8181",
        warehouse: str = "s3://warehouse/",
    ) -> None:
        self.catalog = load_catalog(
            "iceberg_catalog",
            type="rest",
            uri=catalog_uri,
            warehouse=warehouse,
            **{
                "s3.endpoint": "http://localhost:9000",
                "s3.access-key-id": "admin",
                "s3.secret-access-key": "password",
                "s3.path-style-access": "true",
            },
        )

        self.table = self.catalog.load_table(
            ("checkout", "checkout_events_dlq")
        )

    def quarantine(
        self,
        record: dict[str, Any],
        errors: list[str],
    ) -> None:
        row = {
            "order_id": record.get("order_id"),
            "customer_id": record.get("customer_id"),
            "product_id": record.get("product_id"),
            "amount": record.get("amount"),
            "tax_amount": record.get("tax_amount"),
            "payment_status": record.get("payment_status"),
            "event_timestamp": record.get("event_timestamp"),
            "errors": " | ".join(errors),
            "quarantined_at": datetime.now(timezone.utc),
            "status": "QUARANTINED",
        }

        schema = pa.schema([
            pa.field("order_id", pa.string()),
            pa.field("customer_id", pa.string()),
            pa.field("product_id", pa.string()),
            pa.field("amount", pa.float64()),
            pa.field("tax_amount", pa.float64()),
            pa.field("payment_status", pa.string()),
            pa.field("event_timestamp", pa.timestamp("us",tz="UTC")),
            pa.field("errors", pa.string()),
            pa.field("quarantined_at", pa.timestamp("us", tz="UTC")),
            pa.field("status", pa.string()),
        ])

        arrow_table = pa.Table.from_pylist(
            [row],
            schema=schema,
        )

        self.table.append(arrow_table)
    def read_all(self) -> list[dict[str, Any]]:
        return self.table.scan().to_arrow().to_pylist()
    def exists(self, order_id: str) -> bool:
        rows = (
            self.table.scan()
            .to_arrow()
            .to_pylist()
        )

        return any(
            row.get("order_id") == order_id
            for row in rows
        )