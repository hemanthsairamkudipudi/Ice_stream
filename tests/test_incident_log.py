from remediation.incident_log import IncidentLog


def test_record_and_read_incident(tmp_path):
    log_path = tmp_path / "incidents.jsonl"
    incident_log = IncidentLog(path=str(log_path))

    incident = incident_log.record_incident(
        state="OPEN",
        total_records=100,
        failed_records=5,
        error_rate=0.05,
        threshold=0.02,
        quarantined_records=5,
        failure_reasons=[
            "amount must be >= 0",
            "tax_amount is NULL",
        ],
        action="CIRCUIT_OPENED + QUARANTINE",
    )

    assert incident["incident_id"].startswith("INC-")
    assert incident["state"] == "OPEN"
    assert incident["total_records"] == 100
    assert incident["failed_records"] == 5
    assert incident["quarantined_records"] == 5
    assert incident["resolved_at"] is None

    incidents = incident_log.read_incidents()

    assert len(incidents) == 1
    assert incidents[0]["incident_id"] == incident["incident_id"]


def test_record_resolution(tmp_path):
    log_path = tmp_path / "incidents.jsonl"
    incident_log = IncidentLog(path=str(log_path))

    incident = incident_log.record_incident(
        state="OPEN",
        total_records=100,
        failed_records=5,
        error_rate=0.05,
        threshold=0.02,
        quarantined_records=5,
        failure_reasons=["invalid amount"],
        action="CIRCUIT_OPENED + QUARANTINE",
    )

    resolved = incident_log.record_resolution(
        incident["incident_id"],
        state="CLOSED",
        action="RECOVERY_COMPLETED",
    )

    assert resolved is not None
    assert resolved["state"] == "CLOSED"
    assert resolved["action"] == "RECOVERY_COMPLETED"
    assert resolved["resolved_at"] is not None

    incidents = incident_log.read_incidents()

    assert incidents[0]["state"] == "CLOSED"
    assert incidents[0]["resolved_at"] is not None


def test_record_resolution_unknown_incident(tmp_path):
    log_path = tmp_path / "incidents.jsonl"
    incident_log = IncidentLog(path=str(log_path))

    result = incident_log.record_resolution(
        "INC-NOT-FOUND",
        state="CLOSED",
        action="RECOVERY_COMPLETED",
    )

    assert result is None