import uuid

from remediation.iceberg_dlq import IcebergDLQ


def test_iceberg_dlq_can_be_created():
    dlq = IcebergDLQ()

    assert dlq.table is not None
    assert dlq.table.name() == ("checkout", "checkout_events_dlq")


def test_iceberg_dlq_quarantine_writes_record():
    dlq = IcebergDLQ()

    order_id = f"PYTEST_DLQ_{uuid.uuid4().hex[:8]}"

    record = {
        "order_id": order_id,
        "customer_id": "TEST_CUSTOMER",
        "product_id": "TEST_PRODUCT",
        "amount": -100.0,
        "tax_amount": None,
        "payment_status": "FAILED",
        "event_timestamp": None,
    }

    dlq.quarantine(
        record,
        ["amount must be >= 0"],
    )

    rows = dlq.table.scan().to_arrow().to_pylist()

    matches = [
        row
        for row in rows
        if row["order_id"] == order_id
    ]

    assert len(matches) == 1
    assert matches[0]["amount"] == -100.0
    assert matches[0]["tax_amount"] is None
    assert matches[0]["status"] == "QUARANTINED"
    assert matches[0]["errors"] == "amount must be >= 0"