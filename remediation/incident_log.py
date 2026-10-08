from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class IncidentLog:
    """Persist remediation incidents as JSON Lines records."""

    def __init__(self, path: str = "data/incidents.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record_incident(
        self,
        *,
        state: str,
        total_records: int,
        failed_records: int,
        error_rate: float,
        threshold: float,
        quarantined_records: int,
        failure_reasons: list[str],
        action: str,
    ) -> dict[str, Any]:
        incident = {
            "incident_id": self._generate_incident_id(),
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
            "state": state,
            "total_records": total_records,
            "failed_records": failed_records,
            "error_rate": error_rate,
            "threshold": threshold,
            "quarantined_records": quarantined_records,
            "failure_reasons": failure_reasons,
            "action": action,
        }

        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(incident) + "\n")

        return incident

    def record_resolution(
        self,
        incident_id: str,
        *,
        state: str,
        action: str,
    ) -> dict[str, Any] | None:
        incidents = self.read_incidents()

        for incident in reversed(incidents):
            if incident["incident_id"] == incident_id:
                incident["resolved_at"] = datetime.now(
                    timezone.utc
                ).isoformat()
                incident["state"] = state
                incident["action"] = action

                self._rewrite(incidents)
                return incident

        return None

    def read_incidents(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        incidents: list[dict[str, Any]] = []

        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    incidents.append(json.loads(line))

        return incidents

    def get_active_incident(self) -> dict[str, Any] | None:
        """Return the most recent unresolved incident, if one exists."""
        incidents = self.read_incidents()

        for incident in reversed(incidents):
            if incident.get("state") == "OPEN" and incident.get("resolved_at") is None:
                return incident

        return None

    def get_recent_incidents(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return the most recent incidents, newest first."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        incidents = self.read_incidents()
        return list(reversed(incidents[-limit:]))

    def _rewrite(self, incidents: list[dict[str, Any]]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            for incident in incidents:
                file.write(json.dumps(incident) + "\n")

    @staticmethod
    def _generate_incident_id() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        return f"INC-{timestamp}"