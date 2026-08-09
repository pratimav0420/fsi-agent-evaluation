"""Tests verifying the live spike skips cleanly without configuration."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SPIKE_SCRIPT = (
    Path(__file__).parent.parent.parent / "spikes" / "foundry_process_evaluation" / "run_spike.py"
)


class TestSpikeSkipBehavior:
    """Verify the spike exits gracefully without Azure config."""

    def test_spike_skips_without_env_vars(self) -> None:
        """Spike exits with SKIPPED message when env vars are missing."""
        env = os.environ.copy()
        # Ensure required vars are not set
        env.pop("AZURE_AI_PROJECT_CONNECTION_STRING", None)
        env.pop("AZURE_AI_AGENT_MODEL_DEPLOYMENT", None)

        result = subprocess.run(
            [sys.executable, str(SPIKE_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

        assert result.returncode == 0
        assert "SKIPPED" in result.stdout
        assert "AZURE_AI_PROJECT_CONNECTION_STRING" in result.stdout

    def test_spike_does_not_silently_fallback(self) -> None:
        """Spike never silently produces fake results when config is missing."""
        env = os.environ.copy()
        env.pop("AZURE_AI_PROJECT_CONNECTION_STRING", None)
        env.pop("AZURE_AI_AGENT_MODEL_DEPLOYMENT", None)

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
