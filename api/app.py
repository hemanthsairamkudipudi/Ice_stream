from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.status import RemediationStatus
from quality.engine import DataQualityEngine
from quality.iceberg_reader import read_checkout_records
from remediation.remediation_service import RemediationService
from remediation.incident_log import IncidentLog


app = FastAPI(
    title="IceStream Observability API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            "incident": result["incident"],
        }
    )

    return response

@app.get("/api/v1/incidents")
def incident_history():
    incident_log = IncidentLog()

    incidents = incident_log.get_recent_incidents(limit=20)

    return {
        "count": len(incidents),
        "incidents": incidents,
    }
