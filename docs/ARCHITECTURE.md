# NeoTrader System Architecture

NeoTrader treats OpenBB, TradingAgents, and Paperclip as three synchronized organs of one brain. They are not competing strategies.

```text
                         NEO TRADER
                            BODY
                              |
        +---------------------+---------------------+
        |                     |                     |
      OpenBB             TradingAgents          Paperclip
    PERCEPTION             COGNITION          ORCHESTRATION
        |                     |                     |
        +---------- bidirectional connectors ------+
                              |
                       CONFLUENCE ENGINE
                              |
                     DECISION STATE
                              |
                     R:R / POLICY GATE
                              |
                       EXECUTION GATE
                              |
                           BROKER
                              |
                         OUTCOME
                              |
                     FEEDBACK / MEMORY
                              |
                +-------------+-------------+
                |                           |
             agents                    orchestration
                |                           |
                +---------- next cycle -----+
```

## Connector rule

Every layer connector is bidirectional. Inputs enter through a normalized message contract containing connector, direction, message kind, correlation ID, payload and timestamp. Outputs use the same contract in the opposite direction.

This permits:

- OpenBB → brain: market observations, research data and provenance.
- Brain → OpenBB: requests for additional data/timeframes/fields.
- TradingAgents → brain: specialist analysis, debate and proposal state.
- Brain → TradingAgents: normalized observations, tasks, context and feedback.
- Paperclip → brain: scheduling, task state, agent lifecycle and governance events.
- Brain → Paperclip: task creation, state transitions, results and feedback.
- Execution → brain: acknowledgements, fills, rejects, positions and outcomes.
- Brain → execution: only gated decisions that satisfy policy and risk constraints.

## Confluence

The system does not average independent opinions blindly. It synchronizes evidence into one state. A decision is executable only when direction is not conflicted, confidence clears the configured threshold, and a valid reward/risk opportunity of at least 2R is available.

2R is an economic target/constraint, not a guaranteed win rate.

## Feedback

Every decision gets a correlation ID. The resulting execution/outcome is matched back to that decision. This creates an auditable learning record containing the prediction, context, expected R:R, realized R and outcome.

The current implementation deliberately stops at the execution boundary. Broker-specific execution adapters will be added only after the contracts and feedback loop are validated.

## External integration philosophy

OpenBB already supports agent integration and MCP-based tool access; Paperclip is a control plane for teams of agents and supports MCP tool access at the adapter/runtime boundary. NeoTrader therefore acts as the governed integration layer rather than duplicating either project's internal runtime. citeturn0search0turn0search2turn0search7
