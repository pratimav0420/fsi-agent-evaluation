"""Tests verifying the live spike skips cleanly without configuration."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from spikes.foundry_process_evaluation.run_spike import _validate_live_trajectories

SPIKE_SCRIPT = (
    Path(__file__).parent.parent.parent / "spikes" / "foundry_process_evaluation" / "run_spike.py"
)


class TestSpikeSkipBehavior:
    """Verify the spike exits gracefully without Azure config."""

    def test_spike_skips_without_env_vars(self) -> None:
        """Spike exits with SKIPPED message when env vars are missing."""
        env = os.environ.copy()
        # Ensure required vars are not set
        env.pop("FOUNDRY_PROJECT_ENDPOINT", None)
        env.pop("FOUNDRY_DEPLOYMENT_NAME", None)

        result = subprocess.run(
            [sys.executable, str(SPIKE_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

        assert result.returncode == 0
        assert "SKIPPED" in result.stdout
        assert "FOUNDRY_PROJECT_ENDPOINT" in result.stdout

    def test_spike_does_not_silently_fallback(self) -> None:
        """Spike never silently produces fake results when config is missing."""
        env = os.environ.copy()
        env.pop("FOUNDRY_PROJECT_ENDPOINT", None)
        env.pop("FOUNDRY_DEPLOYMENT_NAME", None)

        result = subprocess.run(
            [sys.executable, str(SPIKE_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

        # Should not contain success indicators
        assert "Findings saved" not in result.stdout
        assert "spike_findings.json" not in result.stdout


class TestLiveTrajectoryValidation:
    """Verify live evidence cannot pass without the required control trajectories."""

    def test_accepts_passing_and_broken_control_paths(self) -> None:
        _validate_live_trajectories(
            {
                "tool_calls": [
                    {"tool_name": "verify_entitlement"},
                    {"tool_name": "get_claim_summary"},
                ]
            },
            {"tool_calls": [{"tool_name": "get_claim_summary"}]},
        )

    def test_rejects_empty_passing_trajectory(self) -> None:
        with pytest.raises(ValueError, match="required deterministic tool sequence"):
            _validate_live_trajectories(
                {"tool_calls": []},
                {"tool_calls": [{"tool_name": "get_claim_summary"}]},
            )

    def test_rejects_negative_control_that_does_not_retrieve(self) -> None:
        with pytest.raises(ValueError, match="negative control was not exercised"):
            _validate_live_trajectories(
                {
                    "tool_calls": [
                        {"tool_name": "verify_entitlement"},
                        {"tool_name": "get_claim_summary"},
                    ]
                },
                {"tool_calls": []},
            )

    def test_rejects_negative_control_with_safe_ordering(self) -> None:
        with pytest.raises(ValueError, match="did not reproduce"):
            _validate_live_trajectories(
                {
                    "tool_calls": [
                        {"tool_name": "verify_entitlement"},
                        {"tool_name": "get_claim_summary"},
                    ]
                },
                {
                    "tool_calls": [
                        {"tool_name": "verify_entitlement"},
                        {"tool_name": "get_claim_summary"},
                    ]
                },
            )
