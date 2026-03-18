# Changelog

Notable config and behavior changes. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

- Nothing yet.

## [0.1.0] – initial tracked release

### Added

- **Src layout** — Bot, runners, and dashboard live under `src/`. Entry: `python3 src/liquidation_bot.py` or `liq_bot_run.sh` from repo root.
- **Configurable workspace** — `LIQ_BOT_WORKSPACE` env (default `~/.openclaw/workspace`) for `liq-bot.env`, state, log, and optional `openclaw.json`. Use a custom path to avoid the openclaw directory.
- **Wallet from mnemonic** — Bot address derived from `LIQUIDATION_BOT_MNEMONIC` only; no hardcoded wallet.
- **Telegram from env** — `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `liq-bot.env` (or `openclaw.json`). Alerts optional.
- **MCP paths** — `DORKFI_MCP_PATH` and `HUMBLE_MCP_PATH` (defaults `~/DorkFiMCP`, `~/HumbleSwapMCP`). Used by runners, dashboard, and Python contracts.
- **Node executable** — `LIQ_BOT_NODE` env for subprocess runners (default `node`).
- **Tests** — Unit tests for profit/threshold logic (`tests/test_liq_logic.py`), optional mock integration tests (`tests/test_integration_mock.py`). Run: `pytest tests/`.
- **Lint/format** — Black (Python), Prettier (dashboard); CI workflow and optional pre-commit.
- **Multi-instance** — Separate `LIQ_BOT_WORKSPACE` dirs and cron lines for test vs prod; no shared state/log.
- **Health/readiness** — Bot writes `liq_bot_last_run.json` each run; dashboard `GET /api/health` and `GET /health` (200 if last run &lt; 15 min, 503 if stale).
- **Docs** — `docs/` (architecture, configuration, dashboard, runners, index); README quickstart for users who don’t use openclaw.

### Changed

- **Cron** — Use `liq_bot_run.sh` with optional `LIQ_BOT_WORKSPACE` set so env/state/log come from the chosen workspace.

[Unreleased]: https://github.com/nautilus-oss/dflb/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nautilus-oss/dflb/releases/tag/v0.1.0
