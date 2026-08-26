# NeoTrader Development & Failure-Feedback Workflow

NeoTrader follows a closed engineering feedback loop. A green-looking code change is not considered complete until the repository's actual validation path confirms it.

## Loop

```text
Plan
  ↓
Implement one bounded change
  ↓
Compile / type-check
  ↓
Run tests
  ↓
Inspect CI status
  ↓
If failed: read the exact failing step + logs
  ↓
Classify root cause
  ↓
Fix the cause, not the symptom
  ↓
Commit
  ↓
Run CI again
  ↓
Only then continue architecture work
```

## Rules

1. Never claim a build passes without checking the actual workflow result.
2. A failed workflow is feedback, not something to ignore or blindly rerun.
3. Inspect the failing job and exact assertion/error before changing code.
4. Separate a bad implementation from a bad test. Tests must assert the contract that the code actually promises.
5. Keep external integrations behind adapters and canonical contracts.
6. Never allow missing/invalid data to become an actionable trading decision.
7. External agents receive observations and produce analysis; execution authority remains outside the analyst layer.
8. Never invent market data, account state, fills, tickets, or provider responses.
9. After an external action is eventually introduced, feed the returned result back into the state/decision cycle.
10. Keep secrets, provider URLs, credentials, and deployment-specific endpoints out of source control.

## Current incident

The first NeoTrader CI run failed because a test expected `NO_EXECUTION_AUTHORITY` while the pipeline correctly short-circuited earlier at `DATA_UNAVAILABLE`. The workflow logs were inspected, the test was corrected to test the unavailable-data invariant separately and the execution-authority invariant with valid data, and CI was hardened to compile the source and install the package before testing.
