from quality.engine import DataQualityEngine
from quality.iceberg_reader import read_checkout_records


def main() -> None:
    records = read_checkout_records()

    print(f"Records read from Iceberg: {len(records)}")

    engine = DataQualityEngine()
    result = engine.validate_batch(records)

    print("\nData Quality Result")
    print("-------------------")
    print(f"Passed       : {result.passed}")
    print(f"NULL tax rate: {result.null_tax_rate:.2%}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f" - {error}")
    else:
        print("Errors       : None")


if __name__ == "__main__":
    main()