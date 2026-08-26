from neotrader import (
    DataQuality,
    Decision,
    NeoTraderPipeline,
    NullDataLayer,
    PaperclipAdapter,
    TradingAgentsAdapter,
)


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


def test_analyst_cannot_create_execution_authority():
    result = pipeline().run("BTCUSD")
    assert result.decision is Decision.NO_TRADE
    assert "NO_EXECUTION_AUTHORITY" in result.provenance


def test_confidence_contract():
    from neotrader.contracts import AnalysisResult

    try:
        AnalysisResult(thesis="bad", confidence=1.1)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid confidence must be rejected")
