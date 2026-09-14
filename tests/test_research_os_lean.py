from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest

from evals_to_outcomes.research_os_lean import (
    CheckpointDecision,
    LeanProfileError,
    append_attempt_intent,
    append_attempt_terminal,
    budget_allows,
    classify_checkpoint_issue,
    load_lean_profile,
    read_attempt_log,
    reconcile_attempts,
)

REQUEST_A = "a" * 64
REQUEST_B = "b" * 64
RAW_A = "c" * 64


def test_default_profile_has_scientific_core_and_optional_assurance() -> None:
    profile = load_lean_profile()
    assert profile["profile_id"] == "lean-default-v1"
    assert profile["default_for_new_studies"] is True
    assert profile["mandatory_scientific_core"] == [
        "PROSPECTIVE_PROTOCOL",
        "DATA_IDENTITY_LINEAGE",
        "LABEL_BLINDING",
        "SCORER_VALIDATION",
        "BUDGET_CAP",
        "APPEND_ONLY_ATTEMPT_LOG",
        "DATASET_COMPLETENESS",
        "REPRODUCIBLE_ANALYSIS",
    ]
    assert profile["optional_high_assurance"]["enabled_by_default"] == []


def test_profile_rejects_a_missing_core_control(tmp_path: Path) -> None:
    profile = load_lean_profile()
    profile["mandatory_scientific_core"].remove("LABEL_BLINDING")
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile), encoding="utf-8")
    with pytest.raises(LeanProfileError, match="mandatory core"):
        load_lean_profile(path)


@pytest.mark.parametrize(
    "kind",
    [
        "MISSING_CREDENTIAL",
        "TRANSPORT_FAILURE",
        "PROVIDER_SCHEMA_FAILURE",
        "ENVIRONMENT_FAILURE",
        "FORMATTING_METADATA_FAILURE",
    ],
)
def test_known_operational_issue_gets_one_in_checkpoint_repair(kind: str) -> None:
    assert (
        classify_checkpoint_issue(
            kind,
            provider_action_known=True,
            repair_batches_used=0,
            safe_fallback_available=False,
        )
        == CheckpointDecision.REPAIR_WITHIN_CHECKPOINT
    )


def test_repair_exhaustion_uses_fallback_or_closes_checkpoint() -> None:
    assert (
        classify_checkpoint_issue(
            "TRANSPORT_FAILURE",
            provider_action_known=True,
            repair_batches_used=1,
            safe_fallback_available=True,
        )
        == CheckpointDecision.RECORD_AND_CONTINUE_WITH_FALLBACK
    )
    assert (
        classify_checkpoint_issue(
            "TRANSPORT_FAILURE",
            provider_action_known=True,
            repair_batches_used=1,
            safe_fallback_available=False,
        )
        == CheckpointDecision.CLOSE_CHECKPOINT_OPERATIONAL_STOP
    )


@pytest.mark.parametrize(
    "kind",
    [
        "SCIENTIFIC_SCOPE_CHANGE",
        "CLAIM_CHANGE",
        "NEW_COST",
        "SECURITY_PRIVACY_CHANGE",
        "UNSAFE_AMBIGUITY",
    ],
)
def test_owner_boundary_changes_stop_for_owner(kind: str) -> None:
    assert (
        classify_checkpoint_issue(
            kind,
            provider_action_known=True,
            repair_batches_used=0,
            safe_fallback_available=True,
        )
        == CheckpointDecision.STOP_FOR_OWNER
    )


def test_unknown_provider_action_stops_even_for_operational_issue() -> None:
    assert (
        classify_checkpoint_issue(
            "MISSING_CREDENTIAL",
            provider_action_known=False,
            repair_batches_used=0,
            safe_fallback_available=True,
        )
        == CheckpointDecision.STOP_FOR_OWNER
    )


def test_simple_attempt_log_reconciles_complete_dataset_and_budget(tmp_path: Path) -> None:
    log = tmp_path / "attempts.jsonl"
    append_attempt_intent(
        log,
        attempt_id="attempt-a",
        request_sha256=REQUEST_A,
        reserved_cost_usd="0.30",
        budget_cap_usd="1",
        recorded_at="2026-09-10T01:00:00Z",
    )
    append_attempt_terminal(
        log,
        attempt_id="attempt-a",
        request_sha256=REQUEST_A,
        outcome="SUCCESS",
        provider_contacted=True,
        raw_response_sha256=RAW_A,
        observed_cost_usd="0.12",
        included=True,
        exclusion_reason=None,
        recorded_at="2026-09-10T01:01:00Z",
    )

    rows = read_attempt_log(log)
    assert [row["event"] for row in rows] == ["INTENT", "TERMINAL"]
    assert [row["sequence"] for row in rows] == [1, 2]
    reconciliation = reconcile_attempts(
        log, planned_attempt_ids=["attempt-a"], budget_cap_usd="1.00"
    )
    assert reconciliation["observed_spend_usd"] == "0.12"
    assert reconciliation["dataset_complete"] is True
    assert reconciliation["analysis_ready"] is True


def test_pre_provider_failure_can_use_a_fresh_repair_identity(tmp_path: Path) -> None:
    log = tmp_path / "attempts.jsonl"
    append_attempt_intent(
        log,
        attempt_id="attempt-original",
        request_sha256=REQUEST_A,
        reserved_cost_usd="0.30",
        budget_cap_usd="1",
        recorded_at="2026-09-10T01:00:00Z",
    )
    append_attempt_terminal(
        log,
        attempt_id="attempt-original",
        request_sha256=REQUEST_A,
        outcome="OPERATIONAL_FAILURE",
        provider_contacted=False,
        raw_response_sha256=None,
        observed_cost_usd="0",
        included=False,
        exclusion_reason="credential unavailable before provider contact",
        recorded_at="2026-09-10T01:00:01Z",
    )
    append_attempt_intent(
        log,
        attempt_id="attempt-repair-1",
        request_sha256=REQUEST_B,
        reserved_cost_usd="0.30",
        budget_cap_usd="1",
        recorded_at="2026-09-10T01:02:00Z",
    )
    append_attempt_terminal(
        log,
        attempt_id="attempt-repair-1",
        request_sha256=REQUEST_B,
        outcome="SUCCESS",
        provider_contacted=True,
        raw_response_sha256=RAW_A,
        observed_cost_usd="0.10",
        included=True,
        exclusion_reason=None,
        recorded_at="2026-09-10T01:03:00Z",
    )
    reconciliation = reconcile_attempts(
        log,
        planned_attempt_ids=["attempt-original", "attempt-repair-1"],
        budget_cap_usd="1",
    )
    assert reconciliation["terminal_count"] == 2
    assert reconciliation["included_count"] == 1
    assert reconciliation["analysis_ready"] is True


def test_attempt_identity_and_terminal_are_single_use(tmp_path: Path) -> None:
    log = tmp_path / "attempts.jsonl"
    kwargs = {
        "attempt_id": "attempt-a",
        "request_sha256": REQUEST_A,
        "reserved_cost_usd": "0.2",
        "budget_cap_usd": "1",
        "recorded_at": "2026-09-10T01:00:00Z",
    }
    append_attempt_intent(log, **kwargs)
    with pytest.raises(LeanProfileError, match="already used"):
        append_attempt_intent(log, **kwargs)

    terminal = {
        "attempt_id": "attempt-a",
        "request_sha256": REQUEST_A,
        "outcome": "SUCCESS",
        "provider_contacted": True,
        "raw_response_sha256": RAW_A,
        "observed_cost_usd": "0.1",
        "included": True,
        "exclusion_reason": None,
        "recorded_at": "2026-09-10T01:01:00Z",
    }
    append_attempt_terminal(log, **terminal)
    with pytest.raises(LeanProfileError, match="already has a terminal"):
        append_attempt_terminal(log, **terminal)


def test_mismatched_terminal_request_is_rejected_before_append(tmp_path: Path) -> None:
    log = tmp_path / "attempts.jsonl"
    append_attempt_intent(
        log,
        attempt_id="attempt-a",
        request_sha256=REQUEST_A,
        reserved_cost_usd="0.2",
        budget_cap_usd="1",
        recorded_at="2026-09-10T01:00:00Z",
    )
    with pytest.raises(LeanProfileError, match="request identity differs"):
        append_attempt_terminal(
            log,
            attempt_id="attempt-a",
            request_sha256=REQUEST_B,
            outcome="SUCCESS",
            provider_contacted=True,
            raw_response_sha256=RAW_A,
            observed_cost_usd="0.1",
            included=True,
            exclusion_reason=None,
            recorded_at="2026-09-10T01:01:00Z",
        )
    assert [row["event"] for row in read_attempt_log(log)] == ["INTENT"]


def test_ambiguous_external_outcome_is_preserved_but_not_analysis_ready(tmp_path: Path) -> None:
    log = tmp_path / "attempts.jsonl"
    append_attempt_intent(
        log,
        attempt_id="attempt-a",
        request_sha256=REQUEST_A,
        reserved_cost_usd="0.4",
        budget_cap_usd="1",
        recorded_at="2026-09-10T01:00:00Z",
    )
    append_attempt_terminal(
        log,
        attempt_id="attempt-a",
        request_sha256=REQUEST_A,
        outcome="UNKNOWN_EXTERNAL_OUTCOME",
        provider_contacted=None,
        raw_response_sha256=None,
        observed_cost_usd="0.4",
        included=False,
        exclusion_reason="dispatch occurrence cannot be determined",
        recorded_at="2026-09-10T01:01:00Z",
    )
    reconciliation = reconcile_attempts(log, planned_attempt_ids=["attempt-a"], budget_cap_usd="1")
    assert reconciliation["dataset_complete"] is True
    assert reconciliation["ambiguous_attempt_ids"] == ["attempt-a"]
    assert reconciliation["analysis_ready"] is False


def test_budget_admission_and_reservation_overrun(tmp_path: Path) -> None:
    assert (
        budget_allows(
            cap_usd="2", observed_usd="0.5", outstanding_reserved_usd="0", proposed_max_usd="1.5"
        )
        is True
    )
    assert (
        budget_allows(
            cap_usd="2", observed_usd="0.5001", outstanding_reserved_usd="0", proposed_max_usd="1.5"
        )
        is False
    )
    assert (
        budget_allows(
            cap_usd="2", observed_usd="0.5", outstanding_reserved_usd="0.1", proposed_max_usd="1.5"
        )
        is False
    )

    log = tmp_path / "attempts.jsonl"
    append_attempt_intent(
        log,
        attempt_id="attempt-a",
        request_sha256=REQUEST_A,
        reserved_cost_usd="0.1",
        budget_cap_usd="1",
        recorded_at="2026-09-10T01:00:00Z",
    )
    append_attempt_terminal(
        log,
        attempt_id="attempt-a",
        request_sha256=REQUEST_A,
        outcome="SUCCESS",
        provider_contacted=True,
        raw_response_sha256=RAW_A,
        observed_cost_usd="0.2",
        included=True,
        exclusion_reason=None,
        recorded_at="2026-09-10T01:01:00Z",
    )
    reconciliation = reconcile_attempts(log, planned_attempt_ids=["attempt-a"], budget_cap_usd="1")
    assert reconciliation["reservation_exceeded_attempt_ids"] == ["attempt-a"]
    assert reconciliation["analysis_ready"] is False


def test_atomic_admission_counts_concurrent_reservations(tmp_path: Path) -> None:
    log = tmp_path / "attempts.jsonl"
    barrier = Barrier(2)

    def reserve(attempt: str) -> bool:
        barrier.wait()
        try:
            append_attempt_intent(
                log,
                attempt_id=attempt,
                request_sha256=REQUEST_A,
                reserved_cost_usd="0.6",
                budget_cap_usd="1",
                recorded_at="now",
            )
        except LeanProfileError as error:
            assert "budget cap" in str(error)
            return False
        return True

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(reserve, ["a", "b"])) == [False, True]
    assert len(read_attempt_log(log)) == 1


@pytest.mark.parametrize("cost,outstanding", [("0", "0.8"), ("0.2", "0.6"), ("1", "0")])
def test_unknown_terminal_keeps_unsettled_exposure(
    tmp_path: Path, cost: str, outstanding: str
) -> None:
    log = tmp_path / "attempts.jsonl"
    append_attempt_intent(
        log,
        attempt_id="a",
        request_sha256=REQUEST_A,
        reserved_cost_usd="0.8",
        budget_cap_usd="1",
        recorded_at="now",
    )
    append_attempt_terminal(
        log,
        attempt_id="a",
        request_sha256=REQUEST_A,
        outcome="UNKNOWN_EXTERNAL_OUTCOME",
        provider_contacted=None,
        raw_response_sha256=None,
        observed_cost_usd=cost,
        included=False,
        exclusion_reason="dispatch uncertain",
        recorded_at="later",
    )
    report = reconcile_attempts(log, planned_attempt_ids=["a"], budget_cap_usd="1")
    assert report["outstanding_reserved_usd"] == outstanding
    assert report["analysis_ready"] is False
    with pytest.raises(LeanProfileError, match="budget cap"):
        append_attempt_intent(
            log,
            attempt_id="b",
            request_sha256=REQUEST_B,
            reserved_cost_usd="0.3",
            budget_cap_usd="1",
            recorded_at="later",
        )
    assert len(read_attempt_log(log)) == 2


def test_local_included_success_requires_evidence(tmp_path: Path) -> None:
    log = tmp_path / "attempts.jsonl"
    append_attempt_intent(
        log,
        attempt_id="a",
        request_sha256=REQUEST_A,
        reserved_cost_usd="0",
        budget_cap_usd="0",
        recorded_at="now",
    )
    terminal = {
        "attempt_id": "a",
        "request_sha256": REQUEST_A,
        "outcome": "SUCCESS",
        "provider_contacted": False,
        "raw_response_sha256": None,
        "observed_cost_usd": "0",
        "included": True,
        "exclusion_reason": None,
        "recorded_at": "later",
    }
    with pytest.raises(LeanProfileError, match="included success requires"):
        append_attempt_terminal(log, **terminal)
    assert len(read_attempt_log(log)) == 1
    terminal["raw_response_sha256"] = RAW_A
    append_attempt_terminal(log, **terminal)
    assert reconcile_attempts(log, planned_attempt_ids=["a"], budget_cap_usd="0")["analysis_ready"]
