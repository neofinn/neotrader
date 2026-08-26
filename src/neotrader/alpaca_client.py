from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .paper_trading import PaperOrder


@dataclass(frozen=True)
class AlpacaConfig:
    api_key: str
    secret_key: str
    paper: bool = True

    @classmethod
    def from_env(cls) -> "AlpacaConfig":
        api_key = os.getenv("ALPACA_API_KEY", "")
        secret_key = os.getenv("ALPACA_SECRET_KEY", "")
        if not api_key or not secret_key:
            raise RuntimeError("ALPACA_API_KEY and ALPACA_SECRET_KEY are required")
        return cls(api_key=api_key, secret_key=secret_key, paper=True)


class AlpacaPaperClient:
    """Alpaca-only paper trading adapter.

    The client is deliberately paper-only. There is no live URL/configuration path.
    Install alpaca-py on the server and provide paper-account credentials via env.
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
        from alpaca.trading.enums import OrderSide as AlpacaOrderSide, TimeInForce
        from alpaca.trading.requests import MarketOrderRequest

        side = AlpacaOrderSide.BUY if order.side.value == "buy" else AlpacaOrderSide.SELL
        request = MarketOrderRequest(
            symbol=order.symbol,
            qty=order.quantity,
            side=side,
            time_in_force=TimeInForce.DAY,
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
        }

    def account(self) -> Any:
        return self._client.get_account()

    def positions(self) -> list[Any]:
        return list(self._client.get_all_positions())

    def orders(self, limit: int = 50) -> list[Any]:
        from alpaca.trading.requests import GetOrdersRequest
        return list(self._client.get_orders(filter=GetOrdersRequest(limit=limit)))
