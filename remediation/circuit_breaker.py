from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, error_rate_threshold: float = 0.02) -> None:
        if not 0 <= error_rate_threshold <= 1:
            raise ValueError(
                "error_rate_threshold must be between 0 and 1"
            )

        self.error_rate_threshold = error_rate_threshold
        self.state = CircuitState.CLOSED

    def evaluate(
        self,
        total_records: int,
        failed_records: int,
    ) -> CircuitState:
        if total_records <= 0:
            raise ValueError(
                "total_records must be greater than 0"
            )

        if failed_records < 0:
            raise ValueError(
                "failed_records cannot be negative"
            )

        if failed_records > total_records:
            raise ValueError(
                "failed_records cannot exceed total_records"
            )

        error_rate = failed_records / total_records

        if error_rate > self.error_rate_threshold:
            self.state = CircuitState.OPEN
        else:
            self.state = CircuitState.CLOSED

        return self.state

    def begin_recovery(self) -> CircuitState:
        """Move an OPEN circuit into HALF_OPEN for a recovery test."""

        if self.state != CircuitState.OPEN:
            raise ValueError(
                "Recovery can only begin when circuit is OPEN"
            )

        self.state = CircuitState.HALF_OPEN
        return self.state

    def complete_recovery(self, success: bool) -> CircuitState:
        """Close the circuit if recovery succeeds, otherwise reopen it."""

        if self.state != CircuitState.HALF_OPEN:
            raise ValueError(
                "Recovery must be in HALF_OPEN state"
            )

        if success:
            self.state = CircuitState.CLOSED
        else:
            self.state = CircuitState.OPEN

        return self.state

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def error_rate_threshold_percent(self) -> float:
        return self.error_rate_threshold * 100