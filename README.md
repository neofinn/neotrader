# NeoTrader

An independent agentic trading platform built as three integrated layers:

1. **Data — OpenBB**: canonical market and financial data access.
2. **Analyst — TradingAgents**: multi-agent market analysis and thesis generation.
3. **Agentic Orchestration — Paperclip**: agent lifecycle, task routing, state and workflow coordination.

NeoTrader is intentionally separate from NeoFL. No NeoFL strategy, execution, risk, or infrastructure code belongs here unless explicitly introduced later.

## Architecture

```text
                 ┌─────────────────────────┐
                 │       OpenBB DATA       │
                 │ market / financial data │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   CANONICAL DATA BUS    │
                 │ snapshots + provenance  │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   TRADINGAGENTS ANALYST │
                 │ specialists / debate /  │
                 │ thesis / confidence     │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   PAPERCLIP ORCHESTRATOR│
                 │ tasks / agents / state  │
                 │ workflow / feedback     │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   DECISION CONTRACT     │
                 │ trade idea / confidence │
                 │ rationale / provenance  │
                 └────────────┬────────────┘
                              │
                              ▼
                    Execution boundary

Feedback flows back through the orchestration layer into the next analysis cycle.
```

## Current status

**Phase 1: three-layer foundation**

- Canonical contracts defined.
- Provider/agent adapters isolated behind interfaces.
- Safe data → analysis → decision pipeline scaffolded.
- Missing data cannot produce an actionable decision.
- No broker execution authority is present in this foundation.
