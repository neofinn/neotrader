from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass
class OperatorState:
    enabled: bool = False
    paper_only: bool = True
    kill_switch: bool = True
    last_heartbeat: str | None = None
    last_decision: dict[str, Any] | None = None
    counters: dict[str, int] = field(default_factory=lambda: {
        "decisions": 0,
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "rejected": 0,
    })


class OperatorStore:
    """Small atomic JSON state store for the server dashboard/control plane."""

    def __init__(self, path: str = "runtime/operator_state.json") -> None:
        self.path = Path(path)
        self._lock = Lock()
        self.state = self._load()

    def _load(self) -> OperatorState:
        if not self.path.exists():
            return OperatorState()
        try:
            raw = json.loads(self.path.read_text())
            return OperatorState(**raw)
        except (OSError, ValueError, TypeError):
            return OperatorState()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state.__dict__, indent=2))
        tmp.replace(self.path)

    def heartbeat(self) -> None:
        with self._lock:
            self.state.last_heartbeat = datetime.now(timezone.utc).isoformat()
            self._save()

    def set_enabled(self, enabled: bool) -> OperatorState:
        with self._lock:
            # Kill switch always wins.
            self.state.enabled = bool(enabled) and not self.state.kill_switch
            self._save()
            return self.state

    def set_kill_switch(self, active: bool) -> OperatorState:
        with self._lock:
            self.state.kill_switch = bool(active)
            if active:
                self.state.enabled = False
            self._save()
            return self.state

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self.state.__dict__)
