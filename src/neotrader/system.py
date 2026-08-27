from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .connectors import ConnectorMessage, ConnectorRegistry
from .confluence import ConfluenceEngine, ConfluenceState, Direction, LayerSignal
from .feedback import DecisionEvent, FeedbackStore, OutcomeEvent


@dataclass
class NeoTraderSystem:
    """The body-level integration layer connecting the three brain layers bidirectionally."""

    connectors: ConnectorRegistry
    confluence: ConfluenceEngine
    feedback: FeedbackStore

    def publish(self, connector: str, kind: str, correlation_id: str, payload: dict[str, Any]) -> None:
        self.connectors.send(
            ConnectorMessage(
                connector=connector,
                direction="OUTBOUND",
                kind=kind,
                correlation_id=correlation_id,
                payload=payload,
            )
        )

    def ingest(self) -> list[ConnectorMessage]:
        return self.connectors.receive_all()

    def decide(
        self,
        symbol: str,
        correlation_id: str,
        signals: tuple[LayerSignal, ...],
        reward_risk: float | None,
    ) -> ConfluenceState:
        state = self.confluence.evaluate(symbol, signals, reward_risk)
        self.feedback.record_decision(
            DecisionEvent(
                correlation_id=correlation_id,
                symbol=symbol,
                decision=state.consensus.value,
                confidence=state.confidence,
                expected_reward_risk=state.reward_risk,
                context={"reasons": state.reasons},
            )
        )
        return state

    def record_outcome(self, event: OutcomeEvent) -> None:
        self.feedback.record_outcome(event)
