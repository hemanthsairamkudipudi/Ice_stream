from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    Protect the downstream pipeline when the data-error
    rate exceeds the configured threshold.
    """

    def __init__(self, error_rate_threshold: float = 0.02) -> None:
        if not 0 <= error_rate_threshold <= 1:
            raise ValueError(
                "error_rate_threshold must be between 0 and 1"
            )

        self.error_rate_threshold = error_rate_threshold
        self.state = CircuitState.CLOSED

    def evaluate(self, total_records: int, failed_records: int) -> CircuitState:
        if total_records <= 0:
            raise ValueError("total_records must be greater than 0")

        if failed_records < 0:
            raise ValueError("failed_records cannot be negative")

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

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def error_rate_threshold_percent(self) -> float:
        return self.error_rate_threshold * 100