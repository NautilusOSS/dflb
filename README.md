# DorkFi Liquidation Bot

Automated liquidation bot for **DorkFi** lending on **Voi** and **Algorand**: monitors liquidatable positions, checks profitability, executes direct or swap-then-liquidate flows, and optionally alerts via Telegram.

| | |
|--|--|
| **Docs** | [docs/index.md](docs/index.md) — architecture, configuration, runners, dashboard |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) — notable config and behavior changes |
| **Requires** | Python 3, Node.js (runners + dashboard), [DorkFiMCP](https://github.com/nautilus-oss/DorkFiMCP), [HumbleSwapMCP](https://github.com/nautilus-oss/HumbleSwapMCP) |

---

## Repository layout

```
dflb/
├── docs/                 # Architecture, config, API notes
├── liq_bot_run.sh        # Cron-friendly entry (repo root → python3 src/liquidation_bot.py)
├── requirements.txt
├── .env.example          # Template for liq-bot.env (mnemonic only)
└── src/
    ├── liquidation_bot.py
    ├── runners/
    │   ├── algo_liq_runner.mjs    # DorkFiMCP: candidates + liquidation txs
    │   └── swap_liq_runner.mjs   # HumbleSwap + Pact: quotes / swap build
    └── dashboard/
        ├── server.mjs             # http://localhost:8768
        └── index.html
```

---

## Features

- **Multi-chain** — Voi Pool A/B and Algorand Pool A/B
- **Direct liquidation** — Repay with held aUSDC / USDC / VOI / ALGO
- **Swap-and-liquidate** — HumbleSwap (Voi) or Pact (Algorand) when debt token isn’t held
- **Telegram** *(optional)* — Alerts for opportunities, successes, failures, bad debt. See [Telegram setup](docs/configuration.md#telegram-alerts-optional) in docs.
- **Bad debt guard** — Skips collateral &lt; ~50% of debt
- **Profit filters** — Min profit, swap slippage / price-impact caps
- **Dashboard** — Read-only UI: positions, liquidatable, watchlist, bot balances

---

## Flow (swap path)

```
HF < 1, collateral not bad debt
        │
        ▼
Hold debt token? ──YES──► liquidate
        │
        NO (Voi / Algo)
        ▼
Quote swap → no route or unprofitable → skip
        └──► swap → liquidate → (Telegram)
```

---

## Token coverage

| Chain | Direct | Via swap |
|-------|--------|----------|
| **Voi** | aUSDC, VOI, WAD | UNIT, POW, aALGO, aETH, acbBTC |
| **Algorand** | USDC, ALGO | USDC → debt (Pact, where routed) |

---

## Quickstart (no openclaw)

Minimal path: **copy one file, set two env vars, run.** No `~/.openclaw` required.

1. **Clone and install**
   ```bash
   git clone <this-repo> dflb && cd dflb
   pip install -r requirements.txt
   ```
2. **Copy env template and set your mnemonic**
   ```bash
   mkdir -p config
   cp .env.example config/liq-bot.env
   ```
   Edit `config/liq-bot.env` and set **`LIQUIDATION_BOT_MNEMONIC`** (your 25-word Algorand mnemonic). The second “variable” is **`LIQ_BOT_WORKSPACE`**: you pass it when running so the bot uses `config/` instead of `~/.openclaw/workspace`.
3. **Run once** (DorkFiMCP and HumbleSwapMCP must be on disk; defaults `~/DorkFiMCP`, `~/HumbleSwapMCP`, or set `DORKFI_MCP_PATH` / `HUMBLE_MCP_PATH` in `config/liq-bot.env`):
   ```bash
   LIQ_BOT_WORKSPACE="$(pwd)/config" ./liq_bot_run.sh
   ```
   Log and state go to `config/`. For cron, use the same: `LIQ_BOT_WORKSPACE=/path/to/dflb/config /path/to/dflb/liq_bot_run.sh`.

Full options (Telegram, dashboard, MCP paths): [Setup](#setup) below and [docs/configuration.md](docs/configuration.md).

---

## Setup

### 1. Clone & Python

```bash
cd dflb
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
```

### 2. Environment (mnemonic & workspace)

The bot and dashboard read env from a **workspace** directory. Default: **`~/.openclaw/workspace`**. Override with **`LIQ_BOT_WORKSPACE`** to use any path (e.g. `./config`, `/etc/liq-bot`).

**Default layout:**

```bash
mkdir -p ~/.openclaw/workspace
cp .env.example ~/.openclaw/workspace/liq-bot.env
# Edit: set LIQUIDATION_BOT_MNEMONIC (25-word Algorand mnemonic)
```

**Custom path:** set `export LIQ_BOT_WORKSPACE=/path/to/your/config`, put `liq-bot.env` there (and optionally `openclaw.json` for Telegram). Same variable is used by `liq_bot_run.sh` and the dashboard.

- **Wallet address** is derived from the mnemonic (nothing hardcoded).
- State and log files live in the same workspace dir (see [docs/configuration.md](docs/configuration.md)).

### 3. Node runners (DorkFiMCP / HumbleSwapMCP)

`src/runners/*.mjs` load MCP from **`DORKFI_MCP_PATH`** / **`HUMBLE_MCP_PATH`** (see [docs/configuration.md](docs/configuration.md)). The bot invokes Node via **`LIQ_BOT_NODE`** (default `node` from PATH); set to a full path if needed.

### 4. Cron

```bash
chmod +x liq_bot_run.sh
crontab -e
# example: every 5 minutes
*/5 * * * * /absolute/path/to/dflb/liq_bot_run.sh
```

`liq_bot_run.sh` runs from the repo root, uses `LIQ_BOT_WORKSPACE` (default `~/.openclaw/workspace`) for `liq-bot.env` and the log file.

### 5. Dashboard (optional)

```bash
cd src/dashboard && npm install && node server.mjs
# http://localhost:8768
```

Uses the same workspace as the bot (`LIQ_BOT_WORKSPACE` or default) to load `liq-bot.env` and derive **botWallet** and chain balances.

### 6. Telegram alerts (optional)

The bot can send Telegram messages for opportunities, successes, failures, and bad debt. If you skip this, the bot runs normally and simply does not notify. Setup: [docs/configuration.md#telegram-alerts-optional](docs/configuration.md#telegram-alerts-optional).

### 7. Multi-instance & health (optional)

To run **test and prod** side by side, use separate `LIQ_BOT_WORKSPACE` dirs and cron lines (see [Multi-instance](docs/configuration.md#multi-instance-test-vs-prod)). The bot writes **`liq_bot_last_run.json`** in the workspace each run; the dashboard exposes **`GET /api/health`** (200 if last run &lt; 15 min, 503 if stale). See [Health / readiness](docs/configuration.md#health--readiness).

---

## Testing & formatting

- **Tests:** `pytest tests/` or `make test` (unit tests for profit/threshold logic in `tests/test_liq_logic.py`, optional mock integration in `tests/test_integration_mock.py`). Install dev deps: `pip install -e ".[dev]"` (or `pip install pytest`).
- **Python style:** `black src/` to format, `black --check src/` or `make black-check` to verify.
- **Dashboard style:** `cd src/dashboard && npm run format` / `npm run format:check` (Prettier).
- **CI:** `.github/workflows/test-and-lint.yml` runs pytest, black, and Prettier on push/PR. Optional: `pip install pre-commit && pre-commit install` for local hooks.

---

## Dependencies

| Piece | Role |
|-------|------|
| **py-algorand-sdk**, **python-dotenv** | Bot signing, env |
| **DorkFiMCP** | Liquidation builders, candidates, contracts |
| **HumbleSwapMCP** | Voi swaps |
| **algosdk**, **dotenv** (`src/dashboard`) | Dashboard wallet derivation |

---

## Wallet & capital

- Signing account = mnemonic in **`LIQUIDATION_BOT_MNEMONIC`**.
- Typical capital: **aUSDC** (Voi), **USDC** (Algorand), **VOI** for gas.

---

## License / support

Repo layout and behavior are documented under **`docs/`**. For MCP import paths and tuning (thresholds, APIs), start at [docs/configuration.md](docs/configuration.md).
