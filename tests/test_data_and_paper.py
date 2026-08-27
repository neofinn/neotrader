from datetime import datetime, timezone

import pytest

from neotrader.contracts import DataQuality, DataSnapshot
from neotrader.data_sources import ProviderRouter
from neotrader.paper_trading import OrderSide, PaperOrder, SimulatedPaperBroker


class GoodProvider:
    name = "good"

    def snapshot(self, symbol):
        return DataSnapshot(
            symbol=symbol,
            as_of=datetime.now(timezone.utc),
            quality=DataQuality.VALID,
            fields={"last": 100.0},
            sources=(self.name,),
        )


def test_provider_router_preserves_valid_source():
    router = ProviderRouter({"alpaca": GoodProvider()})
    snapshot = router.snapshot("AAPL")
    assert snapshot.quality is DataQuality.VALID
    assert snapshot.sources == ("good",)


def test_two_r_paper_gate():
    broker = SimulatedPaperBroker()
    order = PaperOrder("AAPL", OrderSide.BUY, 1, 100, 99, 102)
    result = broker.submit(order)
    assert result["paper"] is True
    assert result["correlation_id"] == order.correlation_id


def test_sub_two_r_is_rejected():
    broker = SimulatedPaperBroker()
    order = PaperOrder("AAPL", OrderSide.BUY, 1, 100, 99, 101.5)
    with pytest.raises(ValueError, match="below 2R"):
        broker.submit(order)
