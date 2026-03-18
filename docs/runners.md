# Node runners

Scripts live in **`src/runners/`**. Run from **repository root** (paths below assume `dflb/` as cwd). They load MCP code from **`DORKFI_MCP_PATH`** and **`HUMBLE_MCP_PATH`** (defaults `~/DorkFiMCP`, `~/HumbleSwapMCP`). *This local MCP dependency will be replaced by requests to the UluOS gateway service in the future.*

## `algo_liq_runner.mjs`

Bridge between Python and **DorkFiMCP** for Algorand (and same builder for Voi liquidations when invoked with `voi`).

### Dependencies

- `prepareLiquidation` from DorkFiMCP `lib/builders.js`
- `getLiquidationCandidates` from DorkFiMCP `lib/liquidation.js`

### CLI

```bash
# List liquidatable candidates (Algorand by default; chain as 3rd arg)
node src/runners/algo_liq_runner.mjs candidates algorand
```

Stdout: JSON with `candidates` array (and metadata from MCP).

```bash
# Build unsigned liquidation group (base64-encoded txns in JSON)
node src/runners/algo_liq_runner.mjs build <borrower> <collateralSymbol> <debtSymbol> <amountUSD> <senderAddress> <chain>
# chain: algorand | voi
```

Stdout: `{ "transactions": ["base64", ...], "details": … }`  
Stderr on failure: `{ "error": "..." }`

Python decodes each txn, signs with the bot key, submits one group at a time.

---

## `swap_liq_runner.mjs`

Quotes and builds **Voi** swaps (HumbleSwapMCP). Algorand branch is mainly **quote** via **Pact** REST (direct or ALGO hop); `build_swap` is **Voi only**.

### Dependencies

- HumbleSwapMCP: `prepareSwap`, `resolveToken`, `findBestPool`, `getTokenContractId`, `tokens.js`, `pools.js`
- DorkFiMCP: `prepareLiquidation` (for optional `build_liq` command)
- Pact API: `https://api.pact.fi/api` for Algorand route/quote

### CLI

| Command | Args | Behavior |
|---------|------|----------|
| `quote` | `chain fromSymbol toSymbol amountUSD sender` | JSON: `routable`, `dex`, pool info; Algorand includes `priceImpact` when available |
| `build_swap` | `voi fromSymbol toSymbol amountUSD sender` | Returns `transactions` base64 array (Humble; slippage default 2% in code) |
| `build_liq` | `chain borrower collateral debt amountUSD sender` | Same liquidation builder as algo runner |

Examples:

```bash
node src/runners/swap_liq_runner.mjs quote voi aUSDC WAD 100 <YOUR_BOT_ADDRESS>
node src/runners/swap_liq_runner.mjs build_swap voi aUSDC UNIT 50 <sender>
```

### Algorand token registry

`ALGO_TOKENS` in this file maps symbols (USDC, ALGO, WAD, …) to ASA IDs for Pact routing. Extend when adding swap-from assets.

---

## Error handling

Both runners print JSON errors to stderr and exit non-zero. Python parses stdout only on success; failed builds surface as exceptions in logs and Telegram.
