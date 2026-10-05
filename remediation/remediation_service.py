from typing import Any

from remediation.circuit_breaker import CircuitBreaker, CircuitState
from remediation.dlq import DeadLetterQueue


class RemediationService:
    """Coordinate quality failures, circuit breaking, and quarantine."""

    def __init__(
        self,
        error_rate_threshold: float = 0.02,
        dlq_path: str = "data/dlq.jsonl",
    ) -> None:
        self.circuit_breaker = CircuitBreaker(
            error_rate_threshold=error_rate_threshold
        )
        self.dlq = DeadLetterQueue(path=dlq_path)

    def process_batch(
        self,
        records: list[dict[str, Any]],
        record_errors: dict[int, list[str]],
    ) -> dict[str, Any]:
        total_records = len(records)
        failed_records = len(record_errors)

        state = self.circuit_breaker.evaluate(
            total_records=total_records,
            failed_records=failed_records,
        )

        quarantined = 0

        if state == CircuitState.OPEN:
            for index, errors in record_errors.items():
                self.dlq.quarantine(
                    record=records[index],
                    errors=errors,
                )
                quarantined += 1

        return {
            "state": state.value,
            "total_records": total_records,
            "failed_records": failed_records,
            "error_rate": failed_records / total_records,
            "quarantined_records": quarantined,
        }