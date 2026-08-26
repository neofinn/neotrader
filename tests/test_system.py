from neotrader.connectors import ConnectorMessage, ConnectorRegistry, InMemoryConnector
from neotrader.confluence import ConfluenceEngine, Direction, LayerSignal
from neotrader.feedback import FeedbackStore, OutcomeEvent
from neotrader.system import NeoTraderSystem


def make_system():
    registry = ConnectorRegistry()
    registry.register(InMemoryConnector("openbb"))
    registry.register(InMemoryConnector("tradingagents"))
    registry.register(InMemoryConnector("paperclip"))
    registry.register(InMemoryConnector("execution"))
    return NeoTraderSystem(registry, ConfluenceEngine(), FeedbackStore())


def test_connectors_are_bidirectional():
    system = make_system()
    system.publish("openbb", "MARKET_STATE", "c1", {"symbol": "XAUUSD"})
    connector = system.connectors.get("openbb")
    assert connector.outbound[0].direction == "OUTBOUND"

    connector.inject(ConnectorMessage("openbb", "INBOUND", "DATA", "c1", {"ok": True}))
    messages = system.ingest()
    assert messages[0].direction == "INBOUND"


def test_confluence_requires_two_r():
    system = make_system()
    signals = (
        LayerSignal("openbb", Direction.LONG, 0.9),
        LayerSignal("tradingagents", Direction.LONG, 0.9),
        LayerSignal("paperclip", Direction.LONG, 0.9),
    )
    state = system.decide("XAUUSD", "c2", signals, 1.5)
    assert not state.executable
    assert "RISK_REWARD_BELOW_THRESHOLD" in state.reasons


def test_feedback_closes_the_loop():
    system = make_system()
    signals = (LayerSignal("tradingagents", Direction.LONG, 0.9),)
    system.decide("BTCUSD", "c3", signals, 2.0)
    system.record_outcome(OutcomeEvent("c3", "TARGET", 2.0))
    assert len(system.feedback.matched()) == 1
    assert system.feedback.matched()[0][1].realized_r == 2.0
