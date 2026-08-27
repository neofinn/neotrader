import os

import pytest

from neotrader.alpaca_client import AlpacaConfig
from neotrader.paper_trading import OrderSide, PaperOrder


def test_alpaca_config_requires_credentials(monkeypatch):
    monkeypatch.delenv("APCA_API_KEY_ID", raising=False)
    monkeypatch.delenv("APCA_API_SECRET_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        AlpacaConfig.from_env()


def test_alpaca_config_is_always_paper(monkeypatch):
    monkeypatch.setenv("APCA_API_KEY_ID", "paper-key")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "paper-secret")
    config = AlpacaConfig.from_env()
    assert config.paper is True
    assert config.api_key == "paper-key"


def test_paper_order_requires_two_r():
    order = PaperOrder(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=1,
        entry_price=100,
        stop_price=99,
        target_price=102,
    )
    assert order.reward_risk == 2.0
