from pathlib import Path

from fsi_agent_eval.specifications import load_test_cases, validate_catalog


def test_catalog_has_exact_distribution_and_traceability() -> None:
    result = validate_catalog(
        Path("evaluations/specifications/requirements.yaml"),
        Path("evaluations/datasets/seed-cases.yaml"),
    )
    assert result.requirement_count == 10
    assert result.case_count == 20
    assert result.traceability_coverage == 1.0


def test_all_cases_convert_to_adapter_contract() -> None:
    cases = load_test_cases(Path("evaluations/datasets/seed-cases.yaml"))
    assert len(cases) == 20
    assert all(case.all_requirement_ids for case in cases)
