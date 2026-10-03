import os


def get_float(name: str, default: float) -> float:
    value = os.getenv(name, str(default))
    return float(value)


NULL_THRESHOLD = get_float("NULL_THRESHOLD", 0.10)
ERROR_RATE_THRESHOLD = get_float("ERROR_RATE_THRESHOLD", 0.02)


def validate_config() -> None:
    if not 0 <= NULL_THRESHOLD <= 1:
        raise ValueError("NULL_THRESHOLD must be between 0 and 1")

    if not 0 <= ERROR_RATE_THRESHOLD <= 1:
        raise ValueError("ERROR_RATE_THRESHOLD must be between 0 and 1")