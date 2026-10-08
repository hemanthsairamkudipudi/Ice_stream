from typing import Any

from remediation.circuit_breaker import CircuitBreaker, CircuitState
from remediation.dlq import DeadLetterQueue
from remediation.iceberg_dlq import IcebergDLQ
from remediation.incident_log import IncidentLog


class RemediationService:
    """Coordinate quality failures, circuit breaking, quarantine, and incidents."""

    def __init__(
        self,
        error_rate_threshold: float = 0.02,
        dlq_path: str = "data/dlq.jsonl",
        use_iceberg_dlq: bool = False,
        incident_log_path: str = "data/incidents.jsonl",
    ) -> None:
        self.circuit_breaker = CircuitBreaker(
            error_rate_threshold=error_rate_threshold
        )

        self.use_iceberg_dlq = use_iceberg_dlq

        if use_iceberg_dlq:
            self.dlq = IcebergDLQ()
        else:
            self.dlq = DeadLetterQueue(path=dlq_path)

        self.incident_log = IncidentLog(path=incident_log_path)
        self.active_incident_id: str | None = None

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
                record = records[index]

                if self.use_iceberg_dlq:
                    order_id = record.get("order_id")

                    if order_id and self.dlq.exists(order_id):
                        continue

                self.dlq.quarantine(
                    record=record,
                    errors=errors,
                )

                quarantined += 1

        incident = None

        if state == CircuitState.OPEN:
            failure_reasons = sorted(
                {
                    error
                    for errors in record_errors.values()
                    for error in errors
                }
            )

            incident = self.incident_log.record_incident(
                state=state.value,
                total_records=total_records,
                failed_records=failed_records,
                error_rate=failed_records / total_records,
                threshold=self.circuit_breaker.error_rate_threshold,
                quarantined_records=quarantined,
                failure_reasons=failure_reasons,
                action="CIRCUIT_OPENED + QUARANTINE",
            )
            self.active_incident_id = incident["incident_id"]

        return {
            "state": state.value,
            "total_records": total_records,
            "failed_records": failed_records,
            "error_rate": failed_records / total_records,
            "quarantined_records": quarantined,
            "incident": incident,
        }

    def attempt_recovery(
        self,
        records: list[dict[str, Any]],
        record_errors: dict[int, list[str]],
    ) -> dict[str, Any]:
        if self.circuit_breaker.state != CircuitState.OPEN:
            raise ValueError(
                "Recovery can only be attempted when circuit is OPEN"
            )

        self.circuit_breaker.begin_recovery()

        failed_records = len(record_errors)
        total_records = len(records)

        recovery_success = (
            total_records > 0
            and failed_records == 0
        )

        state = self.circuit_breaker.complete_recovery(
            success=recovery_success
        )
        if recovery_success and self.active_incident_id is not None:
            self.incident_log.record_resolution(
            self.active_incident_id,
            state=state.value,
            action="RECOVERY_COMPLETED",
            )
            self.active_incident_id = None

        return {
            "state": state.value,
            "total_records": total_records,
            "failed_records": failed_records,
            "recovery_success": recovery_success,
        }