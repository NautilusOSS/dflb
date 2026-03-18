/**
 * Algorand DorkFi Liquidation Runner
 * Called by liquidation_bot.py via subprocess.
 * MCP path: set DORKFI_MCP_PATH or default ~/DorkFiMCP. This local MCP dependency
 * will be replaced by requests to the UluOS gateway service in the future.
 * Usage: node src/runners/algo_liq_runner.mjs candidates algorand
 *        node src/runners/algo_liq_runner.mjs build ...
 */

import path from 'path';
import os from 'os';
import { pathToFileURL } from 'url';

const _raw = process.env.DORKFI_MCP_PATH || path.join(os.homedir(), 'DorkFiMCP');
const DORKFI = _raw.startsWith('~') ? path.join(os.homedir(), _raw.slice(1)) : _raw;
const builders = await import(pathToFileURL(path.join(DORKFI, 'lib/builders.js')).href);
const liquidation = await import(pathToFileURL(path.join(DORKFI, 'lib/liquidation.js')).href);
const { prepareLiquidation } = builders;
const { getLiquidationCandidates } = liquidation;

const cmd = process.argv[2];

if (cmd === 'candidates') {
  const chain = process.argv[3] || 'algorand';
  try {
    const result = await getLiquidationCandidates(chain, { threshold: 1.0, limit: 50 });
    console.log(JSON.stringify(result));
  } catch (e) {
    console.error(JSON.stringify({ error: e.message }));
    process.exit(1);
  }
} else if (cmd === 'build') {
  const [, , , borrower, collateralSymbol, debtSymbol, amount, sender, chain] = process.argv;
  try {
    const result = await prepareLiquidation(chain || 'algorand', borrower, collateralSymbol, debtSymbol, parseFloat(amount), sender);
    // Return base64 encoded transactions
    const txns = result.transactions.map(t => Buffer.from(t).toString('base64'));
    console.log(JSON.stringify({ transactions: txns, details: result.details }));
  } catch (e) {
    console.error(JSON.stringify({ error: e.message }));
    process.exit(1);
  }
} else {
  console.error(JSON.stringify({ error: `Unknown command: ${cmd}` }));
  process.exit(1);
}
