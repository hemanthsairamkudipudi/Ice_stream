from quality.iceberg_reader import read_checkout_records
from quality.engine import DataQualityEngine
from remediation.remediation_service import RemediationService


def main() -> None:
    # 1. Read real records from Iceberg
    records = read_checkout_records()

    print(f"Records read from Iceberg: {len(records)}")

    # 2. Validate every record individually
    engine = DataQualityEngine()
    record_errors: dict[int, list[str]] = {}

    for index, record in enumerate(records):
        errors = engine.validate_record(record)

        if errors:
            record_errors[index] = errors

    # 3. Run the remediation service
    service = RemediationService(
        error_rate_threshold=0.02,
        use_iceberg_dlq=True,
    )

    result = service.process_batch(
        records=records,
        record_errors=record_errors,
    )

    # 4. Display the result
    print("\nRemediation Result")
    print("------------------")
    print(f"Total records       : {result['total_records']}")
    print(f"Failed records      : {result['failed_records']}")
    print(f"Error rate          : {result['error_rate']:.2%}")
    print(f"Circuit state       : {result['state']}")
    print(f"Quarantined records : {result['quarantined_records']}")

    # 5. Display the actual errors
    if record_errors:
        print("\nDetected Errors")
        print("----------------")

        for index, errors in record_errors.items():
            print(f"Record {index}:")
            for error in errors:
                print(f"  - {error}")

    # 6. Display DLQ contents
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