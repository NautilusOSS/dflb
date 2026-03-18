# Dashboard

Local **DorkFi Liquidation Monitor** — no execution, read-only monitoring.

## Run

```bash
cd src/dashboard && npm install && node server.mjs
```

Open **http://localhost:8768**

Startup loads `liq-bot.env` from `LIQ_BOT_WORKSPACE` (default `~/.openclaw/workspace`) and derives the bot address from `LIQUIDATION_BOT_MNEMONIC` (same as `src/liquidation_bot.py`). Set `LIQ_BOT_WORKSPACE` when using a custom path. Requires DorkFiMCP on disk (update `import` paths when deploying).

## HTTP API

All JSON, `Access-Control-Allow-Origin: *`.

| Route | Method | Description |
|-------|--------|-------------|
| `/api/positions` | GET | All Voi + Algorand positions with borrow &gt; 0 (health, collateral, debt, appId, network) |
| `/api/balances` | GET | `botWallet` (derived address) + VOI, aUSDC, ALGO, USDC sums, USD estimates, `totalUsd` |
| `/api/position-detail` | GET | Query: `address`, `network` (voi\|algorand), `poolId` — Voi: per-market balances from app boxes |
| `/api/health`, `/health` | GET | Readiness: reads `liq_bot_last_run.json` from workspace. 200 if last run &lt; 15 min, 503 if missing/stale. JSON: `ok`, `last_run_utc`, `status`. |

### Data sources

- Positions: `fetchUserHealthAll` (DorkFiMCP)
- Balances: Voi/Algorand algod account endpoints
- Voi spot: Humble API + CoinGecko (ALGO/USD)

## UI sections (index.html)

1. **Stats** — Counts: liquidatable, on-watch, bad debt, est. profit, bot aUSDC / VOI.
2. **Wallet bar** — Same balances as `/api/balances`.
3. **Liquidatable** — HF &lt; 1, collateral rules exclude bad debt; est. profit from close factor + bonus; “Ready” if bot holds enough stable to repay (Voi: aUSDC or VOI value heuristic; Algo: USDC).
4. **Bad debt** — Insolvent / undercollateralized; optional hide dust (&lt;$1 debt).
5. **Watch (Risk radar)** — HF &lt; 1.5, debt ≥ $0.50; cards + table; click card opens **position modal**.

## Pool name map (frontend)

```js
47139778 → Voi Pool A
47139781 → Voi Pool B
3333688282 → Algo Pool A
3345940978 → Algo Pool B
```

## Static assets

`/` serves `index.html`. Optional: `/whale.png` (header image) — add under `src/dashboard/` if missing.

## Server market maps

`server.mjs` duplicates contractId → symbol maps for **Voi Pool A** boxes and **Algorand** pools A/B for decoding box blobs and LT display. Keep in sync with on-chain markets when DorkFi adds assets.
