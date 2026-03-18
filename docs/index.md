# DorkFi Liquidation Bot — Documentation

Automated liquidation tooling for **DorkFi** lending on **Voi** and **Algorand**. This folder expands on the root [README](../README.md) with implementation-focused detail.

## Repository layout

All runnable code lives under **`src/`**:

| Path | Role |
|------|------|
| **`src/liquidation_bot.py`** | Main loop: fetch liquidatable users, profit/bad-debt checks, direct or swap-then-liquidate on Voi; Algorand direct liquidations; Telegram alerts |
| **`src/runners/algo_liq_runner.mjs`** | Subprocess: DorkFi liquidation tx groups + Algorand candidate list (DorkFiMCP) |
| **`src/runners/swap_liq_runner.mjs`** | Subprocess: Voi swap quotes/build via HumbleSwapMCP; Algorand route discovery via Pact API |
| **`src/dashboard/`** | `server.mjs` (port **8768**) + `index.html` — monitor positions, bad debt, risk radar |
| **`liq_bot_run.sh`** | Cron wrapper: repo root → `python3 src/liquidation_bot.py` |

## Quick links

| Doc | Description |
|-----|-------------|
| [Architecture](./architecture.md) | How Python, Node runners, and the dashboard fit together |
| [Configuration](./configuration.md) | Env vars, paths, thresholds, networks; optional [Telegram setup](./configuration.md#telegram-alerts-optional) |
| [Node runners](./runners.md) | Runner CLI (`src/runners/*.mjs`) |
| [Dashboard](./dashboard.md) | Local API, UI sections, pool IDs |

## External dependencies

- **[DorkFiMCP](https://github.com/nautilus-oss/DorkFiMCP)** — `prepareLiquidation`, `getLiquidationCandidates`, `fetchUserHealthAll`, `contracts.json`
- **[HumbleSwapMCP](https://github.com/nautilus-oss/HumbleSwapMCP)** — Voi swap prep (used by `swap_liq_runner.mjs` and indirectly by swap-and-liquidate in Python)
- **algosdk** (Python + Node) — sign and submit transactions
- **DorkFi API** — Voi liquidatable list: `https://dorkfi-api.nautilus.sh/user-health/liquidatable?network=voimain`

## Typical operation

1. **Schedule** — e.g. cron every 5 minutes: `liq_bot_run.sh` (or `python3 src/liquidation_bot.py` from repo root).
2. **Voi** — HTTP candidates → per-position logic → direct aUSDC/WAD repay or Humble swap then liquidate.
3. **Algorand** — Node runner lists candidates → Python checks balances → liquidate via runner-built txns.
4. **Dashboard** — Optional: `cd src/dashboard && node server.mjs`.

For setup commands, see the root [README](../README.md#setup).
