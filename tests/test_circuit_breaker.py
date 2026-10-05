import pytest

from remediation.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
)


def test_circuit_starts_closed():
    breaker = CircuitBreaker()

    assert breaker.state == CircuitState.CLOSED
    assert breaker.is_open is False


def test_low_error_rate_keeps_circuit_closed():
    breaker = CircuitBreaker(error_rate_threshold=0.02)

    state = breaker.evaluate(
        total_records=100,
        failed_records=1,
    )

    assert state == CircuitState.CLOSED
    assert breaker.is_open is False


def test_error_rate_exactly_at_threshold_stays_closed():
    breaker = CircuitBreaker(error_rate_threshold=0.02)

    state = breaker.evaluate(
        total_records=100,
        failed_records=2,
    )

    assert state == CircuitState.CLOSED


def test_error_rate_above_threshold_opens_circuit():
    breaker = CircuitBreaker(error_rate_threshold=0.02)

    state = breaker.evaluate(
        total_records=100,
        failed_records=3,
    )

    assert state == CircuitState.OPEN
    assert breaker.is_open is True


def test_zero_failed_records_stays_closed():
    breaker = CircuitBreaker()

    state = breaker.evaluate(
        total_records=100,
        failed_records=0,
    )

    assert state == CircuitState.CLOSED


def test_invalid_total_records():
    breaker = CircuitBreaker()

    with pytest.raises(ValueError):
        breaker.evaluate(
            total_records=0,
            failed_records=0,
        )


def test_negative_failed_records():
    breaker = CircuitBreaker()

    with pytest.raises(ValueError):
        breaker.evaluate(
            total_records=100,
            failed_records=-1,
        )


def test_failed_records_cannot_exceed_total():
    breaker = CircuitBreaker()

    with pytest.raises(ValueError):
        breaker.evaluate(
            total_records=100,
            failed_records=101,
        )


def test_custom_threshold():
    breaker = CircuitBreaker(
        error_rate_threshold=0.10
    )

    state = breaker.evaluate(
        total_records=100,
        failed_records=11,
    )

    assert state == CircuitState.OPEN