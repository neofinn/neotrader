# NeoTrader Data + Paper Trading Plan

## Provider strategy

OpenBB remains the canonical data integration layer. Its provider-extension architecture allows sources to be added or removed without changing the core system.

Initial provider preference:

1. **Alpaca** — real-time/historical US equities/options/crypto plus a directly compatible paper-trading environment.
2. **Polygon** — secondary market-data provider for cross-checking and broader coverage where credentials/subscription permit.
3. **FMP** — fundamental/company data where appropriate.
4. **yfinance** — research/fallback only; not treated as sole execution-grade truth.
5. **Public macro sources** exposed through OpenBB — e.g. government/economic series for macro context.

The router preserves source provenance and refuses to convert provider failure or invalid data into a trade.

## Paper trading

Alpaca paper trading is the first execution target because its paper environment is explicitly separate from live trading and uses a separate endpoint/credential set. The application must never silently fall back to a live endpoint.

Paper orders require:

- valid market snapshot
- synchronized decision/confluence state
- defined entry
- defined invalidation/stop
- defined target
- reward/risk >= 2.0
- correlation ID linking observation → decision → order → result

Paper trading is a simulation, not proof of live performance. Alpaca documents limitations including market impact, information leakage, latency/slippage and queue-position effects.

## Current state

The codebase now contains provider routing and an Alpaca paper-broker boundary, plus a deterministic simulated paper broker for tests. Actual Alpaca paper execution requires paper-account credentials/configuration and the concrete SDK client wiring; credentials must be supplied through runtime secrets, never committed to Git.
