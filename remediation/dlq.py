import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DeadLetterQueue:
    """Persist invalid records for later remediation."""

    def __init__(self, path: str = "data/dlq.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def quarantine(
        self,
        record: dict[str, Any],
        errors: list[str],
    ) -> None:
        entry = {
            "record": record,
            "errors": errors,
            "status": "QUARANTINED",
            "quarantined_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        with self.path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(entry, default=str) + "\n"
            )

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        entries = []

        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    entries.append(json.loads(line))

        return entries