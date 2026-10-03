from typing import Any

from quality.config import NULL_THRESHOLD, validate_config
from quality.rules import (
    check_amount,
    check_required_columns,
    check_tax_amount,
)


class QualityResult:
    def __init__(
        self,
        passed: bool,
        errors: list[str],
        null_tax_rate: float,
    ) -> None:
        self.passed = passed
        self.errors = errors
        self.null_tax_rate = null_tax_rate

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "null_tax_rate": self.null_tax_rate,
        }


class DataQualityEngine:
    """Validate checkout events against IceStream data-quality rules."""

    def __init__(self, null_threshold: float = NULL_THRESHOLD) -> None:
        validate_config()

        if not 0 <= null_threshold <= 1:
            raise ValueError("null_threshold must be between 0 and 1")

        self.null_threshold = null_threshold

    def validate_record(self, record: dict[str, Any]) -> list[str]:
        errors = []

        errors.extend(check_required_columns(record))
        errors.extend(check_amount(record))
        errors.extend(check_tax_amount(record))

        return errors

    def validate_batch(
        self,
        records: list[dict[str, Any]],
    ) -> QualityResult:
        if not records:
            return QualityResult(
                passed=True,
                errors=[],
                null_tax_rate=0.0,
            )

        errors: list[str] = []

        for index, record in enumerate(records):
            record_errors = self.validate_record(record)

            for error in record_errors:
                errors.append(f"record[{index}]: {error}")

        null_tax_count = sum(
            1 for record in records
            if record.get("tax_amount") is None
        )

        null_tax_rate = null_tax_count / len(records)

        if null_tax_rate > self.null_threshold:
            errors.append(
                f"tax_amount NULL rate "
                f"{null_tax_rate:.2%} exceeds threshold "
                f"{self.null_threshold:.2%}"
            )

        return QualityResult(
            passed=len(errors) == 0,
            errors=errors,
            null_tax_rate=null_tax_rate,
        )