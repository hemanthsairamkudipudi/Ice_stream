from remediation.remediation_service import RemediationService
from remediation.incident_log import IncidentLog

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

def test_high_error_rate_creates_incident(tmp_path):
    incident_path = tmp_path / "incidents.jsonl"

    service = RemediationService(
        error_rate_threshold=0.02,
        incident_log_path=str(incident_path),
    )

    records = [
        {"order_id": "ORD001", "amount": 100},
        {"order_id": "ORD002", "amount": -50},
        {"order_id": "ORD003", "amount": -20},
        {"order_id": "ORD004", "amount": 200},
    ]

    record_errors = {
        1: ["amount must be >= 0"],
        2: ["amount must be >= 0"],
    }

    result = service.process_batch(
        records=records,
        record_errors=record_errors,
    )

    assert result["state"] == "OPEN"
    assert result["failed_records"] == 2
    assert result["quarantined_records"] == 2

    assert result["incident"] is not None
    assert result["incident"]["state"] == "OPEN"
    assert result["incident"]["total_records"] == 4
    assert result["incident"]["failed_records"] == 2
    assert result["incident"]["quarantined_records"] == 2
    assert result["incident"]["threshold"] == 0.02
    assert result["incident"]["action"] == (
        "CIRCUIT_OPENED + QUARANTINE"
    )

    incident_log = IncidentLog(path=str(incident_path))
    incidents = incident_log.read_incidents()

    assert len(incidents) == 1
    assert incidents[0]["incident_id"] == result["incident"]["incident_id"]


def test_low_error_rate_does_not_create_incident(tmp_path):
    incident_path = tmp_path / "incidents.jsonl"

    service = RemediationService(
        error_rate_threshold=0.02,
        incident_log_path=str(incident_path),
    )

    records = [
        {"order_id": f"ORD{i:03d}", "amount": 100}
        for i in range(100)
    ]

    records[1]["amount"] = -50

    record_errors = {
        1: ["amount must be >= 0"],
    }

    result = service.process_batch(
        records=records,
        record_errors=record_errors,
    )

    assert result["state"] == "CLOSED"
    assert result["failed_records"] == 1
    assert result["error_rate"] == 0.01
    assert result["incident"] is None

    incident_log = IncidentLog(path=str(incident_path))
    assert incident_log.read_incidents() == []


def test_successful_recovery_resolves_incident(tmp_path):
    incident_path = tmp_path / "incidents.jsonl"

    service = RemediationService(
        error_rate_threshold=0.02,
        incident_log_path=str(incident_path),
    )

    records = [
        {"order_id": "ORD001", "amount": 100},
        {"order_id": "ORD002", "amount": -50},
        {"order_id": "ORD003", "amount": -20},
        {"order_id": "ORD004", "amount": 200},
    ]

    record_errors = {
        1: ["amount must be >= 0"],
        2: ["amount must be >= 0"],
    }

    # First, open the circuit and create an incident.
    result = service.process_batch(
        records=records,
        record_errors=record_errors,
    )

    assert result["state"] == "OPEN"
    assert result["incident"] is not None

    incident_id = result["incident"]["incident_id"]

    # Recovery batch has no errors.
    recovery_result = service.attempt_recovery(
        records=records,
        record_errors={},
    )

    assert recovery_result["state"] == "CLOSED"
    assert recovery_result["recovery_success"] is True

    incident_log = IncidentLog(path=str(incident_path))
    incidents = incident_log.read_incidents()

    assert len(incidents) == 1

    incident = incidents[0]

    assert incident["incident_id"] == incident_id
    assert incident["state"] == "CLOSED"
    assert incident["resolved_at"] is not None
    assert incident["action"] == "RECOVERY_COMPLETED"

def test_failed_recovery_keeps_incident_open(tmp_path):
    incident_path = tmp_path / "incidents.jsonl"

    service = RemediationService(
        error_rate_threshold=0.02,
        incident_log_path=str(incident_path),
    )

    records = [
        {"order_id": "ORD001", "amount": 100},
        {"order_id": "ORD002", "amount": -50},
        {"order_id": "ORD003", "amount": -20},
        {"order_id": "ORD004", "amount": 200},
    ]

    record_errors = {
        1: ["amount must be >= 0"],
        2: ["amount must be >= 0"],
    }

    # Open the circuit and create the incident.
    result = service.process_batch(
        records=records,
        record_errors=record_errors,
    )

    assert result["state"] == "OPEN"
    assert result["incident"] is not None

    incident_id = result["incident"]["incident_id"]

    # Recovery still has an error, so recovery must fail.
    recovery_result = service.attempt_recovery(
        records=records,
        record_errors={1: ["amount must be >= 0"]},
    )

    assert recovery_result["state"] == "OPEN"
    assert recovery_result["recovery_success"] is False

    incident_log = IncidentLog(path=str(incident_path))
    incidents = incident_log.read_incidents()

    assert len(incidents) == 1

    incident = incidents[0]

    assert incident["incident_id"] == incident_id
    assert incident["state"] == "OPEN"
    assert incident["resolved_at"] is None
    assert incident["action"] == "CIRCUIT_OPENED + QUARANTINE"