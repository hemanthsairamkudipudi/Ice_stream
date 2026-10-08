import threading
import uuid
from datetime import datetime, timezone

import pyarrow as pa

from quality.iceberg_reader import load_checkout_table, read_checkout_records


def build_record(writer_name: str, test_id: str) -> pa.Table:
    unique_id = f"CONCURRENT-{test_id}-{writer_name}-{uuid.uuid4().hex[:8]}"

    return pa.table(
        {
            "order_id": [unique_id],
            "customer_id": [f"{test_id}-{writer_name}"],
            "product_id": [f"PRODUCT-{writer_name}"],
            "amount": [100.0],
            "tax_amount": [18.0],
            "payment_status": ["SUCCESS"],
            "event_timestamp": [
                datetime.now(timezone.utc)
            ],
        }
    )


def append_record(
    writer_name: str,
    test_id: str,
    errors: list[Exception],
) -> None:
    try:
        table = load_checkout_table()
        record = build_record(writer_name, test_id)

        table.append(
            record,
            snapshot_properties={
                "test": "iceberg-concurrency",
                "test_id": test_id,
                "writer": writer_name,
            },
        )

    except Exception as exc:
        errors.append(exc)


def test_concurrent_iceberg_writes():
    test_id = f"TEST-{uuid.uuid4().hex[:8]}"
    errors: list[Exception] = []

    writer_1 = threading.Thread(
        target=append_record,
        args=("WRITER-1", test_id, errors),
    )

    writer_2 = threading.Thread(
        target=append_record,
        args=("WRITER-2", test_id, errors),
    )

    writer_1.start()
    writer_2.start()

    writer_1.join()
    writer_2.join()

    assert not errors, f"Concurrent Iceberg writes failed: {errors}"

    records = read_checkout_records()

    writer_1_records = [
        record
        for record in records
        if record["customer_id"] == f"{test_id}-WRITER-1"
    ]

    writer_2_records = [
        record
        for record in records
        if record["customer_id"] == f"{test_id}-WRITER-2"
    ]

    assert len(writer_1_records) == 1
    assert len(writer_2_records) == 1