from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .paper_trading import PaperOrder

PAPER_BASE_URL = "https://paper-api.alpaca.markets"


@dataclass(frozen=True)
class AlpacaConfig:
    api_key: str
    secret_key: str
    paper: bool = True

    @classmethod
    def from_env(cls) -> "AlpacaConfig":
        # Support both Alpaca's documented names and the shorter NeoTrader names.
        api_key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY", "")
        secret_key = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_SECRET_KEY", "")
        if not api_key or not secret_key:
            raise RuntimeError("APCA_API_KEY_ID/APCA_API_SECRET_KEY are required")
        return cls(api_key=api_key, secret_key=secret_key, paper=True)


class AlpacaPaperClient:
    """Alpaca-only paper trading adapter.

    Live trading is intentionally impossible through this adapter. Credentials are
    supplied only through the server environment and are never persisted by NeoTrader.
    """

    def __init__(self, config: AlpacaConfig) -> None:
        self.config = config
        if not config.paper:
            raise ValueError("NeoTrader only permits Alpaca paper trading")

        try:
            from alpaca.trading.client import TradingClient
        except ImportError as exc:
            raise RuntimeError("alpaca-py is required for Alpaca paper trading") from exc

        self._client = TradingClient(config.api_key, config.secret_key, paper=True)

    def submit_paper_order(self, order: PaperOrder) -> dict[str, Any]:
        """Submit an entry with its 2R target and invalidation as one bracket order."""
        from alpaca.trading.enums import OrderClass, OrderSide as AlpacaOrderSide, TimeInForce
        from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, TakeProfitRequest

        if order.reward_risk < 2.0:
            raise ValueError("paper order rejected: reward/risk below 2R")
        if order.entry_price <= 0 or order.stop_price <= 0 or order.target_price <= 0:
            raise ValueError("entry, stop and target prices must be positive")

        side = AlpacaOrderSide.BUY if order.side.value == "buy" else AlpacaOrderSide.SELL
        request = MarketOrderRequest(
            symbol=order.symbol,
            qty=order.quantity,
            side=side,
            time_in_force=TimeInForce.DAY,
            order_class=OrderClass.BRACKET,
            take_profit=TakeProfitRequest(limit_price=order.target_price),
            stop_loss=StopLossRequest(stop_price=order.stop_price),
            client_order_id=order.correlation_id,
        )
        result = self._client.submit_order(request)
        return {
            "status": "submitted",
            "paper": True,
            "order_id": str(result.id),
            "client_order_id": str(getattr(result, "client_order_id", order.correlation_id)),
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "entry_price": order.entry_price,
            "stop_price": order.stop_price,
            "target_price": order.target_price,
            "reward_risk": order.reward_risk,
        }

    def account(self) -> Any:
        return self._client.get_account()

    def positions(self) -> list[Any]:
        return list(self._client.get_all_positions())

    def orders(self, limit: int = 50) -> list[Any]:
        from alpaca.trading.requests import GetOrdersRequest
        return list(self._client.get_orders(filter=GetOrdersRequest(limit=limit)))

    def account_config(self) -> Any:
        return self._client.get_account_configurations()

    def cancel_all_orders(self) -> Any:
        return self._client.cancel_orders()
