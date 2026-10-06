from fastapi import FastAPI

from api.status import RemediationStatus
from quality.engine import DataQualityEngine
from quality.iceberg_reader import read_checkout_records
from remediation.remediation_service import RemediationService


app = FastAPI(
    title="IceStream Observability API",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "icestream-observability-api",
    }


@app.get("/api/v1/remediation/status")
def remediation_status() -> dict:
    records = read_checkout_records()

    quality_engine = DataQualityEngine()

    record_errors: dict[int, list[str]] = {}

    for index, record in enumerate(records):
        errors = quality_engine.validate_record(record)

        if errors:
            record_errors[index] = errors

    remediation_service = RemediationService(
        error_rate_threshold=0.02,
        use_iceberg_dlq=True,
    )

    result = remediation_service.process_batch(
        records=records,
        record_errors=record_errors,
    )

    status = RemediationStatus(
        remediation_service.circuit_breaker
    )

    response = status.get_status()

    response.update(
        {
            "total_records": result["total_records"],
            "failed_records": result["failed_records"],
            "error_rate": result["error_rate"],
            "quarantined_records": result["quarantined_records"],
        }
    )

    return response