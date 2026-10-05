import os


ERROR_RATE_THRESHOLD = float(
    os.getenv("ERROR_RATE_THRESHOLD", "0.02")
)


def validate_config() -> None:
    if not 0 <= ERROR_RATE_THRESHOLD <= 1:
        raise ValueError(
            "ERROR_RATE_THRESHOLD must be between 0 and 1"
        )