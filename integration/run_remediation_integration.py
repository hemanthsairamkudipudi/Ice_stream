from quality.iceberg_reader import read_checkout_records
from quality.engine import DataQualityEngine
from remediation.remediation_service import RemediationService


def validate_records(
    records: list[dict],
) -> dict[int, list[str]]:
    """Validate every record and return errors by record index."""
    engine = DataQualityEngine()
    record_errors: dict[int, list[str]] = {}

    for index, record in enumerate(records):
        errors = engine.validate_record(record)

        if errors:
            record_errors[index] = errors

    return record_errors


def main() -> None:
    # ============================================================
    # 1. Read real records from Iceberg
    # ============================================================
    records = read_checkout_records()

    print(f"Records read from Iceberg: {len(records)}")

    # ============================================================
    # 2. Validate the real Iceberg data
    # ============================================================
    record_errors = validate_records(records)

    print("\nInitial Quality Check")
    print("---------------------")
    print(f"Failed records: {len(record_errors)}")

    for index, errors in record_errors.items():
        print(f"Record {index}:")
        for error in errors:
            print(f"  - {error}")

    # ============================================================
    # 3. Run remediation on the real data
    # ============================================================
    service = RemediationService(
        error_rate_threshold=0.02,
        use_iceberg_dlq=True,
    )

    result = service.process_batch(
        records=records,
        record_errors=record_errors,
    )

    print("\nRemediation Result")
    print("------------------")
    print(f"Total records       : {result['total_records']}")
    print(f"Failed records      : {result['failed_records']}")
    print(f"Error rate          : {result['error_rate']:.2%}")
    print(f"Circuit state       : {result['state']}")
    print(f"Quarantined records : {result['quarantined_records']}")

    # ============================================================
    # 4. Display incident information
    # ============================================================
    incident = result.get("incident")

    if incident:
        print("\nIncident")
        print("--------")
        print(f"Incident ID : {incident['incident_id']}")
        print(f"State       : {incident['state']}")
        print(f"Action      : {incident['action']}")

    # ============================================================
    # 5. Recovery simulation
    #
    # IMPORTANT:
    # We do NOT modify the actual Iceberg table here.
    #
    # We simulate successful remediation by removing the detected
    # validation errors from the in-memory validation result.
    # ============================================================
    print("\nRecovery Simulation")
    print("-------------------")
    print("Using corrected in-memory validation results.")
    print("The Iceberg source table is NOT modified.")

    recovered_record_errors: dict[int, list[str]] = {}

    recovery_result = service.attempt_recovery(
        records=records,
        record_errors=recovered_record_errors,
    )

    print("\nRecovery Result")
    print("---------------")
    print(f"Recovery success : {recovery_result['recovery_success']}")
    print(f"Failed records  : {recovery_result['failed_records']}")
    print(f"Circuit state   : {recovery_result['state']}")

    # ============================================================
    # 6. Verify recovery
    # ============================================================
    if (
        recovery_result["recovery_success"]
        and recovery_result["state"] == "CLOSED"
    ):
        print("\nRecovery verification: PASSED")
        print("Circuit transitioned OPEN -> HALF_OPEN -> CLOSED.")
    else:
        print("\nRecovery verification: FAILED")

    # ============================================================
    # 7. Verify incident resolution
    # ============================================================
    recent_incidents = service.incident_log.get_recent_incidents(limit=5)

    print("\nIncident History")
    print("----------------")

    for entry in recent_incidents:
        print(
            f"{entry.get('incident_id')} | "
            f"state={entry.get('state')} | "
            f"resolved_at={entry.get('resolved_at')}"
        )

    active_incident = service.incident_log.get_active_incident()

    if active_incident is None:
        print("\nIncident resolution verification: PASSED")
        print("No unresolved active incident remains.")
    else:
        print("\nIncident resolution verification: FAILED")
        print(
            f"Active incident remains: "
            f"{active_incident.get('incident_id')}"
        )

    # ============================================================
    # 8. Display DLQ contents
    # ============================================================
    entries = service.dlq.read_all()

    print("\nDLQ Summary")
    print("-----------")
    print(f"DLQ records: {len(entries)}")

    for entry in entries:
        print(f" - {entry.get('order_id')}")
        print(f"   Status: {entry.get('status')}")
        print(f"   Errors: {entry.get('errors')}")


if __name__ == "__main__":
    main()