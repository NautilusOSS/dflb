# Configuration

## Secrets & env

| Variable | Purpose |
|----------|---------|
| `LIQUIDATION_BOT_MNEMONIC` | 25-word Algorand mnemonic; **bot wallet address is derived from this** (Python + dashboard) |
| `LIQ_BOT_WORKSPACE` | Optional. Directory for `liq-bot.env`, state file, log file, and (if set) `openclaw.json` for Telegram. Default: `~/.openclaw/workspace`. Set to any path to avoid the openclaw directory. |
| `TELEGRAM_BOT_TOKEN` | Optional. Telegram bot token for alerts. If set (e.g. in `liq-bot.env`), used instead of `openclaw.json`. |
| `TELEGRAM_CHAT_ID` | Optional. Telegram chat ID for alerts (see [Telegram alerts (optional)](#telegram-alerts-optional)). |
| `DORKFI_MCP_PATH` | Optional. Path to DorkFiMCP repo (runners, dashboard, Python contracts.json). Default: `~/DorkFiMCP`. *This local MCP dependency will be replaced by requests to the UluOS gateway service in the future.* |
| `HUMBLE_MCP_PATH` | Optional. Path to HumbleSwapMCP repo (swap runner only). Default: `~/HumbleSwapMCP`. *Same future replacement via UluOS gateway.* |
| `LIQ_BOT_NODE` | Optional. Node.js executable for subprocess runners (e.g. `node`, `/usr/local/bin/node`). Default: `node` (from PATH). |

**Workspace:** Env file path is `$LIQ_BOT_WORKSPACE/liq-bot.env` (default `~/.openclaw/workspace/liq-bot.env`). Same dir holds state, log, and last-run health file. `liq_bot_run.sh` and the dashboard respect `LIQ_BOT_WORKSPACE`; set it before starting the bot or dashboard when using a custom path.

## Multi-instance (test vs prod)

You can run two bots (e.g. test and prod) without shared state or log collision by using **separate workspaces** and **separate cron entries**.

- **Per workspace:** Each `LIQ_BOT_WORKSPACE` directory has its own `liq-bot.env`, `liq_bot_state.json`, `liq_bot_output.log`, `liq_bot_last_run.json`, and (if used) `openclaw.json`. There is no cross-workspace state or file sharing.
- **Setup:** Create two workspace dirs (e.g. `~/.openclaw/workspace-prod` and `~/.openclaw/workspace-test`). Put a distinct `liq-bot.env` in each (different mnemonic for test if desired, or same; different `TELEGRAM_CHAT_ID` optional). Use different cron lines that set `LIQ_BOT_WORKSPACE` before calling the same `liq_bot_run.sh`:
  ```bash
  # Prod (default or explicit workspace)
  */5 * * * * LIQ_BOT_WORKSPACE=~/.openclaw/workspace-prod /path/to/dflb/liq_bot_run.sh
  # Test
  */5 * * * * LIQ_BOT_WORKSPACE=~/.openclaw/workspace-test /path/to/dflb/liq_bot_run.sh
  ```
- **Dashboard:** Point the dashboard at one workspace via `LIQ_BOT_WORKSPACE` when starting it; it will show that workspace’s bot wallet and (if you add it) health for that instance.

**Templates:** Root [`.env.example`](../.env.example). Put `liq-bot.env` inside your workspace dir.

⚠️ **Never commit** real mnemonics or `.env` files.

## Telegram alerts (optional)

Alerts are **optional**. If you do not configure Telegram, the bot runs as usual and simply does not send any messages.

**What gets sent:** Liquidation opportunities (Voi/Algorand), successful liquidations, failures, and bad-debt detections. All messages use HTML and go to a single chat.

**Setup:**

1. **Create a bot** — In Telegram, message [@BotFather](https://t.me/BotFather), send `/newbot`, follow the prompts. Copy the **bot token** (e.g. `123456:ABC-DEF...`).

2. **Bot token** — Either set **`TELEGRAM_BOT_TOKEN`** in `liq-bot.env` (simplest), or put it in **`openclaw.json`**:
   - **Env:** In `liq-bot.env` add `TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."` (your token from BotFather). No JSON file needed.
   - **File:** If you don't set the env, put the token in `openclaw.json`: if **`LIQ_BOT_WORKSPACE`** is set use `$LIQ_BOT_WORKSPACE/openclaw.json`; otherwise **`~/.openclaw/openclaw.json`** (create `~/.openclaw/` if needed).
   ```json
   {
     "channels": {
       "telegram": {
         "botToken": "YOUR_BOT_TOKEN"
       }
     }
   }
   ```

3. **Chat ID** — Start a chat with your new bot (or add it to a group). To get the chat ID:
   - Send a message to the bot, then open: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`. Look for `"chat":{"id": ...}` — that number is your chat ID.
   - Or use a helper like [@userinfobot](https://t.me/userinfobot) in the chat (for groups the ID is often negative).

4. **Env** — In **`liq-bot.env`** (same file as `LIQUIDATION_BOT_MNEMONIC`), add:
   ```bash
   TELEGRAM_CHAT_ID="123456789"
   ```
   Use your actual chat ID (no quotes needed if numeric).

After this, the next bot run will send alerts to that chat when events occur. To disable alerts again, remove or comment out `TELEGRAM_CHAT_ID` or clear the token (env or `openclaw.json`).

## Python bot (`src/liquidation_bot.py`)

Constants (edit in source as needed):

| Constant | Typical value | Meaning |
|----------|---------------|--------|
| *(wallet)* | — | Set only via `LIQUIDATION_BOT_MNEMONIC` → derived at startup |
| `MAX_PER_TRADE` | 200 | Max USD-like repay per liquidation |
| `MIN_PROFIT` | 0.50 | Skip if estimated profit below this (USD) |
| `MIN_SWAP_PROFIT` | 0.05 | Min profit after swap slippage path |
| `MAX_PRICE_IMPACT` | 0.03 | Quote sanity (3%) |
| `VOI_NODE` | Nodely mainnet | Voi algod REST |
| `ALGO_NODE` | Nodely Algorand | Algorand algod REST |
| `DORKFI_API` | dorkfi-api.nautilus.sh | Voi liquidatable endpoint |
| `AUSDC_VOI` | 302190 | aUSDC ASA on Voi |
| `USDC_ALGO` | 31566704 | USDC on Algorand |

**Load path:** Env/state/log come from `LIQ_BOT_WORKSPACE` (default `~/.openclaw/workspace`). Set `LIQ_BOT_WORKSPACE` to any directory that contains `liq-bot.env` (and optionally `openclaw.json` for Telegram).

**Runners:** `algo_liq_runner.mjs` and `swap_liq_runner.mjs` are under **`src/runners/`** and load DorkFiMCP/HumbleSwapMCP from **`DORKFI_MCP_PATH`** / **`HUMBLE_MCP_PATH`** (defaults `~/DorkFiMCP`, `~/HumbleSwapMCP`). No edit of source paths required when set.

**Contracts:** `CONTRACTS` loaded from `$DORKFI_MCP_PATH/data/contracts.json` (default `~/DorkFiMCP/data/contracts.json`). Used for Algorand market `assetId` / decimals.

## Node runners (`src/runners/`)

Both `.mjs` files load MCP modules from **`DORKFI_MCP_PATH`** and **`HUMBLE_MCP_PATH`** (set in env or `liq-bot.env`). No hardcoded paths; defaults `~/DorkFiMCP`, `~/HumbleSwapMCP`.

**Python calls Node via:** **`LIQ_BOT_NODE`** (default `node` from PATH). Set to a full path if needed (e.g. `/usr/local/bin/node`).

## Dashboard (`src/dashboard/`)

| Setting | Value |
|---------|--------|
| Port | **8768** |
| Bot wallet | Derived from `LIQUIDATION_BOT_MNEMONIC` (same `liq-bot.env` as bot); `/api/balances` includes `botWallet` |
| Voi default pool for box reads | `47139778` (Pool A) |

## Cron (`liq_bot_run.sh`)

From repo root: sources `~/.../liq-bot.env` if present, runs `python3 src/liquidation_bot.py`, appends to `~/.../liq_bot_output.log`. Point cron at the script path under your clone, e.g. `*/5 * * * * /path/to/dflb/liq_bot_run.sh`.

## Health / readiness

The bot writes **`liq_bot_last_run.json`** in the workspace at the end of each run (timestamp in UTC, `status: "ok"`). Use this for monitoring:

- **File:** Check `$LIQ_BOT_WORKSPACE/liq_bot_last_run.json`; if `last_run_utc` is older than your threshold (e.g. 15 minutes), treat as stale.
- **HTTP:** If the dashboard is running, **`GET /api/health`** or **`GET /health`** returns JSON with `last_run_utc` and `status`. Response is **200** when the last run is within 15 minutes, **503** when the file is missing or stale. Use the same `LIQ_BOT_WORKSPACE` for the dashboard as for the bot instance you want to monitor.
