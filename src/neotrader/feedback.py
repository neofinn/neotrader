from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DecisionEvent:
    correlation_id: str
    symbol: str
    decision: str
    confidence: float
    expected_reward_risk: float | None
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class OutcomeEvent:
    correlation_id: str
    result: str
    realized_r: float | None
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FeedbackStore:
    """Append-only decision/outcome memory for later evaluation and learning."""

    def __init__(self) -> None:
        self.decisions: list[DecisionEvent] = []
        self.outcomes: list[OutcomeEvent] = []

    def record_decision(self, event: DecisionEvent) -> None:
        self.decisions.append(event)

    def record_outcome(self, event: OutcomeEvent) -> None:
        self.outcomes.append(event)

    def matched(self) -> list[tuple[DecisionEvent, OutcomeEvent]]:
        outcomes = {o.correlation_id: o for o in self.outcomes}
        return [(d, outcomes[d.correlation_id]) for d in self.decisions if d.correlation_id in outcomes]
