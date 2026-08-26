from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Direction(str, Enum):
    NONE = "NONE"
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(frozen=True)
class LayerSignal:
    layer: str
    direction: Direction
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class ConfluenceState:
    symbol: str
    signals: tuple[LayerSignal, ...]
    consensus: Direction
    confidence: float
    reward_risk: float | None
    executable: bool
    reasons: tuple[str, ...] = ()


class ConfluenceEngine:
    """Synchronizes layer outputs into one decision state; it never places orders."""

    def __init__(self, minimum_confidence: float = 0.70, minimum_reward_risk: float = 2.0) -> None:
        self.minimum_confidence = minimum_confidence
        self.minimum_reward_risk = minimum_reward_risk

    def evaluate(self, symbol: str, signals: tuple[LayerSignal, ...], reward_risk: float | None) -> ConfluenceState:
        directional = [s for s in signals if s.direction is not Direction.NONE]
        if not directional:
            return ConfluenceState(symbol, signals, Direction.NONE, 0.0, reward_risk, False, ("NO_DIRECTION",))

        long_score = sum(s.confidence for s in directional if s.direction is Direction.LONG)
        short_score = sum(s.confidence for s in directional if s.direction is Direction.SHORT)
        consensus = Direction.LONG if long_score > short_score else Direction.SHORT if short_score > long_score else Direction.NONE
        confidence = max(long_score, short_score) / len(directional)

        reasons: list[str] = []
        if consensus is Direction.NONE:
            reasons.append("DIRECTION_CONFLICT")
        if confidence < self.minimum_confidence:
            reasons.append("CONFIDENCE_BELOW_THRESHOLD")
        if reward_risk is None or reward_risk < self.minimum_reward_risk:
            reasons.append("RISK_REWARD_BELOW_THRESHOLD")

        return ConfluenceState(symbol, signals, consensus, confidence, reward_risk, not reasons, tuple(reasons))
