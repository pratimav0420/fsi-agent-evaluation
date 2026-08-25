"""Evidence writers for JSON, Markdown, and JUnit-compatible XML."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from fsi_agent_eval.contracts.evaluation import EvaluationRunEnvelope


def write_evidence(envelope: EvaluationRunEnvelope, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "results.json"
    markdown_path = output_dir / "summary.md"
    junit_path = output_dir / "junit.xml"
    json_path.write_text(envelope.model_dump_json(indent=2), encoding="utf-8")

    lines = [
        f"# {envelope.profile.title()} Evaluation",
        "",
        f"- Agent: `{envelope.agent_version}`",
        f"- Gate: **{envelope.gate.decision.value.upper()}**",
        f"- Summary: {envelope.gate.summary}",
        f"- Cases: {len(envelope.test_case_ids)}",
        "",
        "| Case | Requirement | Evaluator | Severity | Result |",
        "|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {r.test_case_id} | {r.requirement_id} | {r.evaluator_name} | "
        f"{r.severity.value} | {'ERROR' if r.evaluator_error else 'PASS' if r.passed else 'FAIL'} |"
        for r in envelope.evaluations
    )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    suite = ET.Element(
        "testsuite",
        name=envelope.profile,
        tests=str(len(envelope.evaluations)),
        failures=str(sum(not r.passed and not r.evaluator_error for r in envelope.evaluations)),
        errors=str(sum(bool(r.evaluator_error) for r in envelope.evaluations)),
    )
    for result in envelope.evaluations:
        case = ET.SubElement(
            suite, "testcase", classname=result.requirement_id, name=result.evaluator_name
        )
        if result.evaluator_error:
            ET.SubElement(case, "error", message=result.evaluator_error).text = result.message
        elif not result.passed:
            ET.SubElement(
                case, "failure", message=result.message or "Evaluation failed"
            ).text = json.dumps(result.evidence)
    ET.ElementTree(suite).write(junit_path, encoding="utf-8", xml_declaration=True)
    return [json_path, markdown_path, junit_path]
