from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .contracts import DataQuality, DataSnapshot


class MarketDataProvider(Protocol):
    name: str

    def snapshot(self, symbol: str) -> DataSnapshot: ...


@dataclass(frozen=True)
class ProviderPolicy:
    """Provider preference without coupling the brain to a vendor."""

    primary: str = "alpaca"
    secondary: tuple[str, ...] = ("polygon", "fmp", "yfinance")
    require_timestamp: bool = True
    require_source: bool = True


class ProviderRouter:
    """Routes data requests while preserving provider provenance."""

    def __init__(self, providers: dict[str, MarketDataProvider], policy: ProviderPolicy | None = None) -> None:
        self.providers = providers
        self.policy = policy or ProviderPolicy()

    def snapshot(self, symbol: str) -> DataSnapshot:
        names = (self.policy.primary, *self.policy.secondary)
        failures: list[str] = []
        for name in names:
            provider = self.providers.get(name)
            if provider is None:
                continue
            try:
                snapshot = provider.snapshot(symbol)
                if snapshot.quality is DataQuality.VALID:
                    return snapshot
                failures.append(f"{name}:{snapshot.quality.value}")
            except Exception as exc:
                failures.append(f"{name}:{type(exc).__name__}")
        from datetime import datetime, timezone
        return DataSnapshot(
            symbol=symbol,
            as_of=datetime.now(timezone.utc),
            quality=DataQuality.UNAVAILABLE,
            fields={"provider_failures": failures},
            sources=tuple(failures),
        )


class AlpacaMarketDataProvider:
    """Live-data adapter. Credentials stay outside source control."""

    name = "alpaca"

    def __init__(self, client: Any) -> None:
        self.client = client

    def snapshot(self, symbol: str) -> DataSnapshot:
        # The concrete SDK call belongs here; the canonical contract stays vendor-neutral.
        raw = self.client.get_snapshot(symbol)
        from datetime import datetime, timezone
        timestamp = raw.get("timestamp") or datetime.now(timezone.utc)
        return DataSnapshot(
            symbol=symbol,
            as_of=timestamp,
            quality=DataQuality.VALID,
            fields=dict(raw),
            sources=(self.name,),
        )
