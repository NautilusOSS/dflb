#!/bin/bash
# Run from repo root. Uses LIQ_BOT_WORKSPACE for env/state/log; default ~/.openclaw/workspace.
DFLB_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$DFLB_ROOT"
LIQ_BOT_WS="${LIQ_BOT_WORKSPACE:-$HOME/.openclaw/workspace}"
export LIQ_BOT_WORKSPACE="$LIQ_BOT_WS"
source "$LIQ_BOT_WS/liq-bot.env" 2>/dev/null || true
python3 src/liquidation_bot.py >> "$LIQ_BOT_WS/liq_bot_output.log" 2>&1
