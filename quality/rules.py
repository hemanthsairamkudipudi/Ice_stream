from typing import Any


REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "amount",
]


def check_required_columns(record: dict[str, Any]) -> list[str]:
    errors = []

    for column in REQUIRED_COLUMNS:
        if record.get(column) is None:
            errors.append(f"{column} must not be NULL")

    return errors


def check_amount(record: dict[str, Any]) -> list[str]:
    errors = []

    amount = record.get("amount")

    if amount is not None:
        if not isinstance(amount, (int, float)):
            errors.append("amount must be numeric")
        elif amount < 0:
            errors.append("amount must be >= 0")

    return errors


def check_tax_amount(record: dict[str, Any]) -> list[str]:
    errors = []

    tax_amount = record.get("tax_amount")

    if tax_amount is not None:
        if not isinstance(tax_amount, (int, float)):
            errors.append("tax_amount must be numeric")

    return errors