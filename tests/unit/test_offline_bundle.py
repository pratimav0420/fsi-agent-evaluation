from pathlib import Path

from fsi_agent_eval.cli import replay_bundle
from fsi_agent_eval.contracts.evaluation import GateDecision


def test_recorded_live_pass_replays_without_azure(tmp_path: Path) -> None:
    result = replay_bundle(Path("data/offline-bundle/live-pass.json"), tmp_path / "pass")
    assert result.gate.decision == GateDecision.PASS


def test_recorded_broken_order_blocks_without_azure(tmp_path: Path) -> None:
    result = replay_bundle(Path("data/offline-bundle/live-broken-order.json"), tmp_path / "broken")
    assert result.gate.decision == GateDecision.BLOCK
