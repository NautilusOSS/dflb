# Architecture

## High-level flow

```
                    ┌─────────────────────────────────────┐
                    │  src/liquidation_bot.py (Python)    │
                    │  • Voi: DorkFi API + algod           │
                    │  • Algo: algo_liq_runner candidates  │
                    │  • Sign/submit via algosdk           │
                    └───────────┬──────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ DorkFi API    │     │ algo_liq_runner │     │ swap_liq_runner │
│ (Voi liq list)│     │ (src/runners)   │     │ (src/runners)   │
└───────────────┘     │ DorkFiMCP       │     │ Humble + Pact   │
                      └────────┬────────┘     └────────┬────────┘
                               │                       │
                               ▼                       ▼
                      Base64 tx groups           Quote / build_swap
                      (liquidation)              (Voi only build)
```

## Candidate sources

| Chain | Source | Notes |
|-------|--------|--------|
| **Voi** | `GET …/user-health/liquidatable?network=voimain` | JSON `data[]` |
| **Algorand** | `node src/runners/algo_liq_runner.mjs candidates algorand` | Uses DorkFiMCP `getLiquidationCandidates` |

## Processing pipeline (Python)

1. **Filters** — Skip if HF ≥ 1; skip bad debt (collateral &lt; $1 or collateral &lt; 50% of debt).
2. **Sizing** — Repay ≈ `min(50% of debt, MAX_PER_TRADE)` (default cap $200 in code).
3. **Profit** — Voi bonus ~10%, Algorand ~6%; compare to `MIN_PROFIT` / gas estimate.
4. **Direct vs swap** — If wallet holds debt token → build liquidation only. Else on Voi, quote `aUSDC`/`WAD` → debt via `swap_liq_runner`; if routable and profitable → `build_swap` → confirm → `liquidate_voi`.
5. **Symbol detection (Voi)** — When API omits symbols, bot reads pool **box** storage (`detect_symbols_voi`) mapped by `VOI_POOL_A_MARKETS` contract IDs.

## Dashboard (separate process)

- **`src/dashboard/server.mjs`** calls DorkFiMCP `fetchUserHealthAll('voi'|'algorand')` for all borrowing positions.
- UI classifies rows: liquidatable (HF &lt; 1 & profitable), bad debt, watch (HF &lt; 1.5).
- Does **not** submit transactions; monitoring only.

## State & alerts

- **State file** — JSON list of past liquidations (path configured in Python, often under workspace).
- **Telegram** — Bot token from `openclaw.json`; chat ID from env `TELEGRAM_CHAT_ID` (alerts: opportunity, success, failure, bad debt).
