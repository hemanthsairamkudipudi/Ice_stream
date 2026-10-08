from fastapi.testclient import TestClient
from remediation.incident_log import IncidentLog
from api.app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "icestream-observability-api",
    }


def test_remediation_status_includes_incident_information(
    monkeypatch,
    tmp_path,
):
    incident_path = tmp_path / "incidents.jsonl"

    class FakeRemediationService:
        def __init__(
            self,
            error_rate_threshold,
            use_iceberg_dlq,
        ):
            from remediation.remediation_service import (
                RemediationService,
            )

            self._service = RemediationService(
                error_rate_threshold=error_rate_threshold,
                incident_log_path=str(incident_path),
                use_iceberg_dlq=False,
            )

        def process_batch(self, records, record_errors):
            return self._service.process_batch(
                records=records,
                record_errors=record_errors,
            )

        @property
        def circuit_breaker(self):
            return self._service.circuit_breaker

    def fake_read_checkout_records():
        return [
            {"order_id": "ORD001", "amount": 100},
            {"order_id": "ORD002", "amount": -50},
            {"order_id": "ORD003", "amount": -20},
            {"order_id": "ORD004", "amount": 200},
        ]

    def fake_validate_record(self,record):
        if record["amount"] < 0:
            return ["amount must be >= 0"]
        return []

    monkeypatch.setattr(
        "api.app.DataQualityEngine.validate_record",
        fake_validate_record,
)

    monkeypatch.setattr(
        "api.app.read_checkout_records",
        fake_read_checkout_records,
    )

    monkeypatch.setattr(
        "api.app.RemediationService",
        FakeRemediationService,
    )

    response = client.get("/api/v1/remediation/status")

    assert response.status_code == 200

    data = response.json()

    assert data["state"] == "OPEN"
    assert data["total_records"] == 4
    assert data["failed_records"] == 2
    assert data["quarantined_records"] == 2

    assert data["incident"] is not None
    assert data["incident"]["state"] == "OPEN"
    assert data["incident"]["failed_records"] == 2
    assert data["incident"]["quarantined_records"] == 2
    assert data["incident"]["action"] == (
        "CIRCUIT_OPENED + QUARANTINE"
    )

def test_incident_history_endpoint(monkeypatch, tmp_path):
    incident_path = tmp_path / "incidents.jsonl"

    incident_log = IncidentLog(path=str(incident_path))

    incident_log.record_incident(
        state="OPEN",
        total_records=100,
        failed_records=5,
        error_rate=0.05,
        threshold=0.02,
        quarantined_records=5,
        failure_reasons=["amount must be >= 0"],
        action="CIRCUIT_OPENED + QUARANTINE",
    )

    monkeypatch.setattr(
        "api.app.IncidentLog",
        lambda: IncidentLog(path=str(incident_path)),
    )

    response = client.get("/api/v1/incidents")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["incidents"]) == 1
    assert data["incidents"][0]["state"] == "OPEN"
    assert data["incidents"][0]["action"] == "CIRCUIT_OPENED + QUARANTINE"