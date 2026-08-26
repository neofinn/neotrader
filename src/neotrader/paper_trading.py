from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol
import uuid


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class PaperOrder:
    symbol: str
    side: OrderSide
    quantity: float
    entry_price: float
    stop_price: float
    target_price: float
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def risk_per_unit(self) -> float:
        return abs(self.entry_price - self.stop_price)

    @property
    def reward_per_unit(self) -> float:
        return abs(self.target_price - self.entry_price)

    @property
    def reward_risk(self) -> float:
        risk = self.risk_per_unit
        return self.reward_per_unit / risk if risk else 0.0


class PaperBroker(Protocol):
    def submit(self, order: PaperOrder) -> dict[str, Any]: ...


class SimulatedPaperBroker:
    """Deterministic broker for development. Never routes to a live venue."""

    def __init__(self) -> None:
        self.orders: list[PaperOrder] = []

    def submit(self, order: PaperOrder) -> dict[str, Any]:
        if order.quantity <= 0:
            raise ValueError("quantity must be positive")
        if order.reward_risk < 2.0:
            raise ValueError("paper order rejected: reward/risk below 2R")
        self.orders.append(order)
        return {
            "status": "accepted",
            "paper": True,
            "order_id": str(uuid.uuid4()),
            "correlation_id": order.correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class AlpacaPaperBroker:
    """Adapter boundary for Alpaca's paper endpoint; no live endpoint is permitted."""

    PAPER_BASE_URL = "https://paper-api.alpaca.markets"

    def __init__(self, client: Any) -> None:
        self.client = client

    def submit(self, order: PaperOrder) -> dict[str, Any]:
        # The concrete alpaca-py order request belongs here.
        # The adapter intentionally exposes no live-account URL.
        return self.client.submit_paper_order(order)
