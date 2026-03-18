"""
Pure profit/threshold logic for the liquidation bot. No I/O or env.
Used by tests and can be used by liquidation_bot to keep logic testable.
"""

# Defaults aligned with liquidation_bot.py
DEFAULT_MAX_PER_TRADE = 200.0
DEFAULT_MIN_PROFIT = 0.50
DEFAULT_MIN_SWAP_PROFIT = 0.05
DEFAULT_EST_GAS = 0.10
REPAY_PCT = 0.50
BAD_DEBT_COLLATERAL_FLOOR = 1.0
BAD_DEBT_COLLATERAL_DEBT_RATIO = 0.5


def is_bad_debt(collateral_usd: float, debt_usd: float) -> bool:
    """True if position should be skipped as bad debt (collateral too low)."""
    if collateral_usd < BAD_DEBT_COLLATERAL_FLOOR:
        return True
    if collateral_usd < debt_usd * BAD_DEBT_COLLATERAL_DEBT_RATIO:
        return True
    return False


def repay_amount(
    borrow_usd: float,
    max_per_trade: float = DEFAULT_MAX_PER_TRADE,
    pct: float = REPAY_PCT,
) -> float:
    """Repay amount = min(borrow * pct, max_per_trade)."""
    return min(borrow_usd * pct, max_per_trade)


def liquidation_bonus(chain: str) -> float:
    """Voi ~10%, Algorand ~6%."""
    return 0.10 if chain == "voi" else 0.06


def est_profit_direct(
    repay: float,
    bonus: float,
    est_gas: float = DEFAULT_EST_GAS,
) -> float:
    """Expected profit for direct liquidation: repay * bonus - gas."""
    return repay * bonus - est_gas


def est_profit_swap(
    max_seize: float,
    repay: float,
    swap_cost: float,
    est_gas: float = DEFAULT_EST_GAS,
) -> float:
    """Expected profit after swap: max_seize - repay - swap_cost - gas."""
    return max_seize - repay - swap_cost - est_gas


def is_profitable_direct(
    est_profit: float,
    min_profit: float = DEFAULT_MIN_PROFIT,
) -> bool:
    """True if direct liquidation meets minimum profit."""
    return est_profit >= min_profit


def is_profitable_swap(
    est_profit: float,
    min_swap_profit: float = DEFAULT_MIN_SWAP_PROFIT,
) -> bool:
    """True if swap-then-liquidate meets minimum profit."""
    return est_profit >= min_swap_profit
