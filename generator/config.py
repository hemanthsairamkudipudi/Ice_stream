import os


def get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {"true", "1", "yes", "y", "on"}


EVENTS_PER_SECOND = float(os.getenv("EVENTS_PER_SECOND", "10"))
TOTAL_EVENTS = int(os.getenv("TOTAL_EVENTS", "100"))

CONTINUOUS_MODE = get_bool("CONTINUOUS_MODE", False)

NULL_TAX_RATE = float(os.getenv("NULL_TAX_RATE", "0.03"))
SCHEMA_DRIFT_RATE = float(os.getenv("SCHEMA_DRIFT_RATE", "0.01"))
DUPLICATE_RATE = float(os.getenv("DUPLICATE_RATE", "0.01"))
INVALID_VALUE_RATE = float(os.getenv("INVALID_VALUE_RATE", "0.01"))


def validate_config() -> None:
    if EVENTS_PER_SECOND <= 0:
        raise ValueError("EVENTS_PER_SECOND must be greater than 0")

    if TOTAL_EVENTS < 0:
        raise ValueError("TOTAL_EVENTS cannot be negative")

    rates = {
        "NULL_TAX_RATE": NULL_TAX_RATE,
        "SCHEMA_DRIFT_RATE": SCHEMA_DRIFT_RATE,
        "DUPLICATE_RATE": DUPLICATE_RATE,
        "INVALID_VALUE_RATE": INVALID_VALUE_RATE,
    }

    for name, rate in rates.items():
        if not 0 <= rate <= 1:
            raise ValueError(f"{name} must be between 0 and 1")