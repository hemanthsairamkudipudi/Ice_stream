from api.status import RemediationStatus
from remediation.circuit_breaker import CircuitBreaker, CircuitState


def test_status_starts_closed():
    circuit = CircuitBreaker(error_rate_threshold=0.02)
    status = RemediationStatus(circuit)

    result = status.get_status()

    assert result["state"] == "CLOSED"
    assert result["is_open"] is False
    assert result["threshold_percent"] == 2.0


def test_status_reports_open_circuit():
    circuit = CircuitBreaker(error_rate_threshold=0.02)

    circuit.evaluate(
        total_records=10,
        failed_records=2,
    )

    status = RemediationStatus(circuit)
    result = status.get_status()

    assert result["state"] == "OPEN"
    assert result["is_open"] is True


def test_status_reports_half_open_circuit():
    circuit = CircuitBreaker(error_rate_threshold=0.02)

    circuit.evaluate(
        total_records=10,
        failed_records=2,
    )

    circuit.begin_recovery()

    status = RemediationStatus(circuit)
    result = status.get_status()

    assert result["state"] == "HALF_OPEN"
    assert result["is_open"] is False