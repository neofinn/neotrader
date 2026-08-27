from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .contracts import AnalysisResult, DataSnapshot, DataQuality, Decision, Recommendation


class DataLayer(ABC):
    @abstractmethod
    def snapshot(self, symbol: str) -> DataSnapshot:
        raise NotImplementedError


class AnalystLayer(ABC):
    @abstractmethod
    def analyze(self, snapshot: DataSnapshot) -> AnalysisResult:
        raise NotImplementedError


class OrchestratorLayer(ABC):
    @abstractmethod
    def recommend(self, snapshot: DataSnapshot, analysis: AnalysisResult) -> Recommendation:
        raise NotImplementedError


class NullDataLayer(DataLayer):
    """Safe default: until a real provider is connected, nothing is tradable."""

    def snapshot(self, symbol: str) -> DataSnapshot:
        from datetime import datetime, timezone

        return DataSnapshot(
            symbol=symbol,
            as_of=datetime.now(timezone.utc),
            quality=DataQuality.UNAVAILABLE,
            sources=("null",),
        )


class TradingAgentsAdapter(AnalystLayer):
    """Boundary for the TradingAgents implementation; no execution authority."""

    def analyze(self, snapshot: DataSnapshot) -> AnalysisResult:
        if not snapshot.actionable:
            return AnalysisResult(
                thesis="Analysis blocked because market data is not actionable.",
                confidence=0.0,
                provenance=("TradingAgentsAdapter", "DATA_UNAVAILABLE"),
            )
        return AnalysisResult(
            thesis="Adapter connected; analyst implementation pending.",
            confidence=0.0,
            provenance=("TradingAgentsAdapter", "UNIMPLEMENTED"),
        )


class PaperclipAdapter(OrchestratorLayer):
    """Boundary for Paperclip orchestration and agent lifecycle management."""

    def recommend(self, snapshot: DataSnapshot, analysis: AnalysisResult) -> Recommendation:
        # Safety invariant: orchestration cannot turn unavailable data into a trade.
        if not snapshot.actionable:
            return Recommendation(
                symbol=snapshot.symbol,
                decision=Decision.NO_TRADE,
                confidence=0.0,
                thesis="NO_TRADE: data unavailable or invalid.",
                data_quality=snapshot.quality,
                provenance=("PaperclipAdapter", "DATA_UNAVAILABLE"),
            )
        return Recommendation(
            symbol=snapshot.symbol,
            decision=Decision.NO_TRADE,
            confidence=analysis.confidence,
            thesis=analysis.thesis,
            data_quality=snapshot.quality,
            provenance=("PaperclipAdapter", "NO_EXECUTION_AUTHORITY"),
        )


@dataclass
class NeoTraderPipeline:
    data: DataLayer
    analyst: AnalystLayer
    orchestrator: OrchestratorLayer

    def run(self, symbol: str) -> Recommendation:
        snapshot = self.data.snapshot(symbol)
        analysis = self.analyst.analyze(snapshot)
        return self.orchestrator.recommend(snapshot, analysis)
