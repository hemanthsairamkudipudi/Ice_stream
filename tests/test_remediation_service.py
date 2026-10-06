from remediation.remediation_service import RemediationService


def test_low_error_rate_keeps_pipeline_closed(tmp_path):
    service = RemediationService(
        error_rate_threshold=0.02,
        dlq_path=str(tmp_path / "dlq.jsonl"),
    )

    records = [
        {"order_id": "ORD001"},
        {"order_id": "ORD002"},
        {"order_id": "ORD003"},
        {"order_id": "ORD004"},
        {"order_id": "ORD005"},
        {"order_id": "ORD006"},
        {"order_id": "ORD007"},
        {"order_id": "ORD008"},
        {"order_id": "ORD009"},
        {"order_id": "ORD010"},
    ]

    result = service.process_batch(
        records,
        {
            0: ["invalid amount"],
        },
    )

    assert result["state"] == "OPEN"


def test_high_error_rate_opens_and_quarantines(tmp_path):
    service = RemediationService(
        error_rate_threshold=0.02,
        dlq_path=str(tmp_path / "dlq.jsonl"),
    )

    records = [
        {"order_id": "BAD001"},
        {"order_id": "BAD002"},
        {"order_id": "GOOD001"},
    ]

    result = service.process_batch(
        records,
        {
            0: ["negative amount"],
            1: ["NULL tax_amount"],
        },
    )

    assert result["state"] == "OPEN"
    assert result["failed_records"] == 2
    assert result["quarantined_records"] == 2

    entries = service.dlq.read_all()

    assert len(entries) == 2
    assert entries[0]["record"]["order_id"] == "BAD001"
    assert entries[1]["record"]["order_id"] == "BAD002"


def test_no_errors_keeps_pipeline_closed(tmp_path):
    service = RemediationService(
        error_rate_threshold=0.02,
        dlq_path=str(tmp_path / "dlq.jsonl"),
    )

    records = [
        {"order_id": "GOOD001"},
        {"order_id": "GOOD002"},
        {"order_id": "GOOD003"},
    ]

    result = service.process_batch(
        records,
        {},
    )

    assert result["state"] == "CLOSED"
    assert result["failed_records"] == 0
    assert result["quarantined_records"] == 0
def test_successful_recovery_closes_circuit(tmp_path):
    service = RemediationService(
        error_rate_threshold=0.02,
        dlq_path=str(tmp_path / "dlq.jsonl"),
    )

    bad_records = [
        {"order_id": "BAD001"},
        {"order_id": "GOOD001"},
    ]

    service.process_batch(
        bad_records,
        {0: ["invalid amount"]},
    )

    clean_records = [
        {"order_id": "GOOD002"},
        {"order_id": "GOOD003"},
    ]

    result = service.attempt_recovery(
        clean_records,
        {},
    )

    assert result["recovery_success"] is True
    assert result["state"] == "CLOSED"


def test_failed_recovery_reopens_circuit(tmp_path):
    service = RemediationService(
        error_rate_threshold=0.02,
        dlq_path=str(tmp_path / "dlq.jsonl"),
    )

    bad_records = [
        {"order_id": "BAD001"},
        {"order_id": "GOOD001"},
    ]

    service.process_batch(
        bad_records,
        {0: ["invalid amount"]},
    )

    still_bad_records = [
        {"order_id": "BAD002"},
        {"order_id": "GOOD002"},
    ]

    result = service.attempt_recovery(
        still_bad_records,
        {0: ["amount must be >= 0"]},
    )

    assert result["recovery_success"] is False
    assert result["state"] == "OPEN"