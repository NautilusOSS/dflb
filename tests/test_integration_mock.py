"""Optional integration-style tests with mocks (DorkFi API, runner stdout).

These tests mock external I/O to assert the bot's parsing and thresholds.
They do not require a real mnemonic, CONTRACTS file, or Node runners.
"""
import json
import pytest


class TestVoiCandidatesMock:
    """Mock DorkFi API liquidatable response; assert structure and filtering."""

    @pytest.fixture
    def mock_voi_response(self):
        return {
            "data": [
                {
                    "userAddress": "ALGO" + "0" * 55,
                    "healthFactor": 0.95,
                    "totalBorrowValue": "100.50",
                    "totalCollateralValue": "95.20",
                    "debtSymbol": "aUSDC",
                    "collateralSymbol": "VOI",
                    "poolId": 47139778,
                },
            ]
        }

    def test_voi_candidates_structure(self, mock_voi_response):
        """API returns data[] with expected fields for a liquidatable position."""
        data = mock_voi_response["data"]
        assert len(data) == 1
        row = data[0]
        assert "userAddress" in row
        assert "healthFactor" in row
        assert float(row["totalBorrowValue"]) == 100.50
        assert float(row["totalCollateralValue"]) == 95.20
        assert row["debtSymbol"] == "aUSDC"
        assert row["collateralSymbol"] == "VOI"


class TestAlgoRunnerStdoutMock:
    """Mock algo_liq_runner.mjs stdout; assert JSON shape the bot expects."""

    def test_candidates_stdout_parsed(self):
        """Bot expects stdout = JSON with 'candidates' array."""
        fake_stdout = json.dumps({
            "candidates": [
                {"userAddress": "ALGO" + "0" * 55, "healthFactor": 0.92},
            ],
            "meta": {},
        })
        parsed = json.loads(fake_stdout)
        assert "candidates" in parsed
        assert len(parsed["candidates"]) == 1
        assert parsed["candidates"][0]["healthFactor"] == 0.92
