from typing import Any

from remediation.circuit_breaker import CircuitState, CircuitBreaker


class RemediationStatus:
    """Expose the current remediation state for observability."""

    def __init__(
        self,
        circuit_breaker: CircuitBreaker,
    ) -> None:
        self.circuit_breaker = circuit_breaker

    def get_status(self) -> dict[str, Any]:
        return {
            "state": self.circuit_breaker.state.value,
            "is_open": self.circuit_breaker.is_open,
            "threshold_percent": (
                self.circuit_breaker.error_rate_threshold_percent
            ),
        }