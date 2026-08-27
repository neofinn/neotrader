from datetime import datetime, timezone

from neotrader import (
    DataQuality,
    Decision,
    NeoTraderPipeline,
    NullDataLayer,
    PaperclipAdapter,
    TradingAgentsAdapter,
)
from neotrader.contracts import DataSnapshot


def pipeline():
    return NeoTraderPipeline(
        data=NullDataLayer(),
        analyst=TradingAgentsAdapter(),
        orchestrator=PaperclipAdapter(),
    )


def test_unavailable_data_forces_no_trade():
    result = pipeline().run("XAUUSD")
    assert result.decision is Decision.NO_TRADE
    assert result.data_quality is DataQuality.UNAVAILABLE
    assert not result.executable
    assert "DATA_UNAVAILABLE" in result.provenance


def test_valid_data_still_has_no_execution_authority():
    snapshot = DataSnapshot(
        symbol="BTCUSD",
        as_of=datetime.now(timezone.utc),
        quality=DataQuality.VALID,
    )
    analysis = TradingAgentsAdapter().analyze(snapshot)
    result = PaperclipAdapter().recommend(snapshot, analysis)
    assert result.decision is Decision.NO_TRADE
    assert "NO_EXECUTION_AUTHORITY" in result.provenance
    assert not result.executable


def test_confidence_contract():
    from neotrader.contracts import AnalysisResult

    try:
        AnalysisResult(thesis="bad", confidence=1.1)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid confidence must be rejected")
