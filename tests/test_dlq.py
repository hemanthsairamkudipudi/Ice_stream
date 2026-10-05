from remediation.dlq import DeadLetterQueue


def test_quarantine_writes_invalid_record(tmp_path):
    dlq = DeadLetterQueue(
        path=str(tmp_path / "dlq.jsonl")
    )

    record = {
        "order_id": "ORD_BAD_001",
        "amount": -500.0,
    }

    errors = [
        "amount must be >= 0"
    ]

    dlq.quarantine(record, errors)

    entries = dlq.read_all()

    assert len(entries) == 1
    assert entries[0]["record"] == record
    assert entries[0]["errors"] == errors
    assert entries[0]["status"] == "QUARANTINED"
    assert "quarantined_at" in entries[0]


def test_multiple_records_are_quarantined(tmp_path):
    dlq = DeadLetterQueue(
        path=str(tmp_path / "dlq.jsonl")
    )

    dlq.quarantine(
        {"order_id": "BAD001"},
        ["invalid amount"],
    )

    dlq.quarantine(
        {"order_id": "BAD002"},
        ["NULL tax_amount"],
    )

    entries = dlq.read_all()

    assert len(entries) == 2
    assert entries[0]["record"]["order_id"] == "BAD001"
    assert entries[1]["record"]["order_id"] == "BAD002"


def test_empty_dlq_returns_empty_list(tmp_path):
    dlq = DeadLetterQueue(
        path=str(tmp_path / "dlq.jsonl")
    )

    assert dlq.read_all() == []