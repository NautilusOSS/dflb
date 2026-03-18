"""Unit tests for profit/threshold logic (liq_logic)."""
import pytest

from liq_logic import (
    is_bad_debt,
    repay_amount,
    liquidation_bonus,
    est_profit_direct,
    est_profit_swap,
    is_profitable_direct,
    is_profitable_swap,
    DEFAULT_MIN_PROFIT,
    DEFAULT_MIN_SWAP_PROFIT,
)


class TestBadDebt:
    def test_collateral_below_one_is_bad_debt(self):
        assert is_bad_debt(0.5, 100.0) is True
        assert is_bad_debt(0, 10.0) is True

    def test_collateral_above_floor_and_half_debt_is_ok(self):
        assert is_bad_debt(2.0, 2.0) is False   # coll >= 1, coll >= debt*0.5
        assert is_bad_debt(10.0, 10.0) is False

    def test_collateral_below_half_debt_is_bad_debt(self):
        assert is_bad_debt(10.0, 50.0) is True   # 10 < 25
        assert is_bad_debt(1.0, 5.0) is True    # 1 < 2.5


class TestRepayAmount:
    def test_repay_capped_by_max_per_trade(self):
        assert repay_amount(1000.0, max_per_trade=200.0) == 200.0
        assert repay_amount(500.0, max_per_trade=200.0) == 200.0

    def test_repay_half_borrow_when_below_cap(self):
        assert repay_amount(100.0, max_per_trade=200.0) == 50.0
        assert repay_amount(300.0, max_per_trade=200.0) == 150.0


class TestLiquidationBonus:
    def test_voi_bonus(self):
        assert liquidation_bonus("voi") == 0.10

    def test_algorand_bonus(self):
        assert liquidation_bonus("algorand") == 0.06


class TestEstProfit:
    def test_direct_profit(self):
        # repay=100, bonus=0.10 -> gain 10, minus gas 0.10 -> 9.90
        p = est_profit_direct(100.0, 0.10)
        assert abs(p - 9.90) < 0.001

    def test_swap_profit(self):
        # max_seize 110, repay 100, swap 2, gas 0.10 -> 7.90
        p = est_profit_swap(110.0, 100.0, 2.0)
        assert abs(p - 7.90) < 0.001


class TestProfitableThresholds:
    def test_direct_below_min_profit_skipped(self):
        assert is_profitable_direct(0.30, min_profit=DEFAULT_MIN_PROFIT) is False
        assert is_profitable_direct(0.50, min_profit=DEFAULT_MIN_PROFIT) is True
        assert is_profitable_direct(1.0, min_profit=DEFAULT_MIN_PROFIT) is True

    def test_swap_below_min_swap_profit_skipped(self):
        assert is_profitable_swap(0.02, min_swap_profit=DEFAULT_MIN_SWAP_PROFIT) is False
        assert is_profitable_swap(0.05, min_swap_profit=DEFAULT_MIN_SWAP_PROFIT) is True
        assert is_profitable_swap(0.10, min_swap_profit=DEFAULT_MIN_SWAP_PROFIT) is True
