from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DataQuality(str, Enum):
    VALID = "VALID"
    STALE = "STALE"
    INCOMPLETE = "INCOMPLETE"
    UNAVAILABLE = "UNAVAILABLE"
    CONTRADICTORY = "CONTRADICTORY"


class Decision(str, Enum):
    NO_TRADE = "NO_TRADE"
    WATCH = "WATCH"
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(frozen=True)
class DataSnapshot:
    symbol: str
    as_of: datetime
    quality: DataQuality
    fields: dict[str, Any] = field(default_factory=dict)
    sources: tuple[str, ...] = ()

    @property
    def actionable(self) -> bool:
        return self.quality is DataQuality.VALID


@dataclass(frozen=True)
class AnalysisResult:
    thesis: str
    confidence: float
    specialists: dict[str, str] = field(default_factory=dict)
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class Recommendation:
    symbol: str
    decision: Decision
    confidence: float
    thesis: str
    data_quality: DataQuality
    provenance: tuple[str, ...] = ()

    @property
    def executable(self) -> bool:
        return self.decision in {Decision.LONG, Decision.SHORT} and self.data_quality is DataQuality.VALID
