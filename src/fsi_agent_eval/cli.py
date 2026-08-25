"""Run and compare offline FSI agent evaluation profiles."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import TypeAdapter

from fsi_agent_eval.adapters.local import BrokenOrderingAdapter, LocalAgentAdapter
from fsi_agent_eval.adapters.protocol import AgentAdapter, TestCase
from fsi_agent_eval.contracts.agent import AgentRunResult
from fsi_agent_eval.contracts.evaluation import EvaluationRunEnvelope, GateDecision
from fsi_agent_eval.evaluators import decide_gate, evaluate_run
from fsi_agent_eval.reporting import write_evidence
from fsi_agent_eval.specifications import load_test_cases, validate_catalog


def _load_cases(path: Path) -> list[TestCase]:
    if path.suffix in {".yaml", ".yml"}:
        return load_test_cases(path)
    return TypeAdapter(list[TestCase]).validate_json(path.read_text(encoding="utf-8"))


def run_profile(
    adapter: AgentAdapter,
    cases_path: Path,
    output_dir: Path,
    profile: str,
    baseline_identifier: str | None = None,
) -> EvaluationRunEnvelope:
    started = datetime.now(UTC)
    cases = _load_cases(cases_path)
    runs = [adapter.run(case) for case in cases]
    evaluations = [
        result for case, run in zip(cases, runs, strict=True) for result in evaluate_run(case, run)
    ]
    for evaluation, case in (
        (evaluation, case)
        for case in cases
        for evaluation in evaluations
        if evaluation.test_case_id == case.id
    ):
        evaluation.must_pass = bool(case.metadata.get("must_pass", False))
    gate = decide_gate(
        evaluations, agent_version=runs[0].agent_version, run_ids=[run.run_id for run in runs]
    )
    envelope = EvaluationRunEnvelope(
        suite="offline-deterministic",
        profile=profile,
        agent_version=runs[0].agent_version,
        prompt_version=runs[0].prompt_version,
        model_identifier=runs[0].model_identifier,
        baseline_identifier=baseline_identifier,
        test_case_ids=[case.id for case in cases],
        run_ids=[run.run_id for run in runs],
        evaluations=evaluations,
        gate=gate,
        started_at=started,
        completed_at=datetime.now(UTC),
    )
    paths = write_evidence(envelope, output_dir)
    envelope.artifact_paths = [str(path) for path in paths]
    (output_dir / "results.json").write_text(envelope.model_dump_json(indent=2), encoding="utf-8")
    print(gate.summary)
    print(f"Evidence: {output_dir.resolve()}")
    return envelope


def compare_results(baseline_path: Path, candidate_path: Path, output_path: Path) -> int:
    baseline = EvaluationRunEnvelope.model_validate_json(baseline_path.read_text(encoding="utf-8"))
    candidate = EvaluationRunEnvelope.model_validate_json(
        candidate_path.read_text(encoding="utf-8")
    )
    comparison = {
        "schema_version": "1.0",
        "baseline": baseline.agent_version,
        "candidate": candidate.agent_version,
        "baseline_gate": baseline.gate.decision.value,
        "candidate_gate": candidate.gate.decision.value,
        "new_blocking_findings": len(candidate.gate.blocking_results)
        - len(baseline.gate.blocking_results),
        "regression": baseline.gate.decision == GateDecision.PASS
        and candidate.gate.decision != GateDecision.PASS,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(json.dumps(comparison, indent=2))
    return 1 if comparison["regression"] else 0


def replay_bundle(bundle_path: Path, output_dir: Path) -> EvaluationRunEnvelope:
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    run = AgentRunResult.model_validate(payload["run"])
    case = TestCase(
        id=f"REPLAY-{bundle_path.stem.upper()}",
        requirement_id="FSI-AUTH-001",
        requirement_ids=["FSI-TOOL-001", "FSI-TRC-001"],
        conversation_turns=["What is the status of synthetic claim CLM-SPIKE-001?"],
        expected_tool_sequence=["verify_entitlement", "get_claim_summary"],
        metadata={
            "claim_id": "CLM-SPIKE-001",
            "entitlement": "authorized",
            "must_pass": True,
        },
    )
    evaluations = evaluate_run(case, run)
    for evaluation in evaluations:
        evaluation.must_pass = True
    gate = decide_gate(evaluations, agent_version=run.agent_version, run_ids=[run.run_id])
    envelope = EvaluationRunEnvelope(
        suite="recorded-live-replay",
        profile="replay",
        agent_version=run.agent_version,
        prompt_version=run.prompt_version,
        model_identifier=run.model_identifier,
        baseline_identifier=payload.get("schema_version"),
        test_case_ids=[case.id],
        run_ids=[run.run_id],
        evaluations=evaluations,
        gate=gate,
        started_at=run.start_time or datetime.now(UTC),
        completed_at=run.end_time or datetime.now(UTC),
    )
    envelope.artifact_paths = [str(path) for path in write_evidence(envelope, output_dir)]
    (output_dir / "results.json").write_text(envelope.model_dump_json(indent=2), encoding="utf-8")
    print(gate.summary)
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("baseline", "broken"):
        command = subparsers.add_parser(name)
        command.add_argument("--cases", type=Path, default=Path("data/demo/cases.json"))
        command.add_argument("--output", type=Path, default=Path(f"artifacts/{name}"))
    compare = subparsers.add_parser("compare")
    compare.add_argument("--baseline", type=Path, default=Path("artifacts/baseline/results.json"))
    compare.add_argument("--candidate", type=Path, default=Path("artifacts/broken/results.json"))
    compare.add_argument("--output", type=Path, default=Path("artifacts/comparison.json"))
    validate = subparsers.add_parser("validate")
    validate.add_argument(
        "--requirements",
        type=Path,
        default=Path("evaluations/specifications/requirements.yaml"),
    )
    validate.add_argument(
        "--cases", type=Path, default=Path("evaluations/datasets/seed-cases.yaml")
    )
    replay = subparsers.add_parser("replay")
    replay.add_argument("--bundle", type=Path, default=Path("data/offline-bundle/live-pass.json"))
    replay.add_argument("--output", type=Path, default=Path("artifacts/replay"))
    args = parser.parse_args()
    if args.command == "compare":
        return compare_results(args.baseline, args.candidate, args.output)
    if args.command == "validate":
        print(validate_catalog(args.requirements, args.cases).model_dump_json(indent=2))
        return 0
    if args.command == "replay":
        envelope = replay_bundle(args.bundle, args.output)
        return 0 if envelope.gate.decision in {GateDecision.PASS, GateDecision.WARN} else 1
    adapter = LocalAgentAdapter() if args.command == "baseline" else BrokenOrderingAdapter()
    envelope = run_profile(adapter, args.cases, args.output, args.command)
    return 0 if envelope.gate.decision in {GateDecision.PASS, GateDecision.WARN} else 1


if __name__ == "__main__":
    raise SystemExit(main())
