"""Small reusable primitives for the Research OS lean-default profile.

This standalone package supplies profile validation, checkpoint routing, a compact attempt ledger,
atomic budget admission, and completeness reconciliation. Study-specific scientific validation,
provider dispatch, evidence storage, and analysis remain the caller's responsibility.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
from collections.abc import Callable, Iterable, Mapping
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from pathlib import Path
from typing import Any

PROFILE_PATH = Path(__file__).with_name("research_os_lean_default_v1.json")

MANDATORY_SCIENTIFIC_CORE = (
    "PROSPECTIVE_PROTOCOL",
    "DATA_IDENTITY_LINEAGE",
    "LABEL_BLINDING",
    "SCORER_VALIDATION",
    "BUDGET_CAP",
    "APPEND_ONLY_ATTEMPT_LOG",
    "DATASET_COMPLETENESS",
    "REPRODUCIBLE_ANALYSIS",
)

OPTIONAL_HIGH_ASSURANCE = (
    "PER_TRANSITION_INDEPENDENT_AUDIT",
    "IMMUTABLE_INTERMEDIATE_PERMISSIONS",
    "MULTIPLE_GO_RECEIPTS",
    "INJECTED_FAULT_SUITE",
    "CRASH_CUSTODY_CEREMONY",
    "ROOT_ONLY_RELEASE_FILES",
)

OPERATIONAL_ISSUE_KINDS = (
    "MISSING_CREDENTIAL",
    "TRANSPORT_FAILURE",
    "PROVIDER_SCHEMA_FAILURE",
    "ENVIRONMENT_FAILURE",
    "FORMATTING_METADATA_FAILURE",
)

OWNER_DECISION_ISSUE_KINDS = (
    "SCIENTIFIC_SCOPE_CHANGE",
    "CLAIM_CHANGE",
    "NEW_COST",
    "SECURITY_PRIVACY_CHANGE",
    "UNSAFE_AMBIGUITY",
)

_PROFILE_FIELDS = {
    "schema_version",
    "profile_id",
    "default_for_new_studies",
    "mandatory_scientific_core",
    "optional_high_assurance",
    "checkpoint_policy",
}
_OPTIONAL_FIELDS = {"available", "enabled_by_default"}
_POLICY_FIELDS = {
    "max_bounded_repair_batches",
    "operational_issue_kinds",
    "owner_decision_issue_kinds",
    "fallback_rule",
}
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,191}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z")
_OUTCOMES = {
    "SUCCESS",
    "OPERATIONAL_FAILURE",
    "SCIENTIFIC_INVALID",
    "UNKNOWN_EXTERNAL_OUTCOME",
}


class LeanProfileError(ValueError):
    """A lean-profile configuration or evidence invariant was violated."""


class CheckpointDecision(StrEnum):
    """The four possible lean checkpoint actions."""

    REPAIR_WITHIN_CHECKPOINT = "REPAIR_WITHIN_CHECKPOINT"
    RECORD_AND_CONTINUE_WITH_FALLBACK = "RECORD_AND_CONTINUE_WITH_FALLBACK"
    CLOSE_CHECKPOINT_OPERATIONAL_STOP = "CLOSE_CHECKPOINT_OPERATIONAL_STOP"
    STOP_FOR_OWNER = "STOP_FOR_OWNER"


def _exact_mapping(value: Any, fields: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise LeanProfileError(f"{label} fields differ")
    return value


def load_lean_profile(path: Path | None = None) -> dict[str, Any]:
    """Load and strictly validate the versioned lean-default profile."""

    profile_path = PROFILE_PATH if path is None else Path(path)
    try:
        value = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LeanProfileError("lean profile is unreadable") from error

    profile = _exact_mapping(value, _PROFILE_FIELDS, "profile")
    if (
        profile["schema_version"] != "research-os-lean-profile-v1"
        or profile["profile_id"] != "lean-default-v1"
        or profile["default_for_new_studies"] is not True
        or type(profile["mandatory_scientific_core"]) is not list
        or tuple(profile["mandatory_scientific_core"]) != MANDATORY_SCIENTIFIC_CORE
    ):
        raise LeanProfileError("lean profile identity or mandatory core differs")

    optional = _exact_mapping(
        profile["optional_high_assurance"], _OPTIONAL_FIELDS, "optional high assurance"
    )
    if (
        type(optional["available"]) is not list
        or type(optional["enabled_by_default"]) is not list
        or tuple(optional["available"]) != OPTIONAL_HIGH_ASSURANCE
        or optional["enabled_by_default"] != []
    ):
        raise LeanProfileError("high-assurance defaults differ")

    policy = _exact_mapping(profile["checkpoint_policy"], _POLICY_FIELDS, "checkpoint policy")
    if (
        type(policy["max_bounded_repair_batches"]) is not int
        or policy["max_bounded_repair_batches"] != 1
        or type(policy["operational_issue_kinds"]) is not list
        or type(policy["owner_decision_issue_kinds"]) is not list
        or tuple(policy["operational_issue_kinds"]) != OPERATIONAL_ISSUE_KINDS
        or tuple(policy["owner_decision_issue_kinds"]) != OWNER_DECISION_ISSUE_KINDS
        or policy["fallback_rule"]
        != "RECORD_AND_CONTINUE_IF_PROSPECTIVELY_ALLOWED_ELSE_CLOSE_CHECKPOINT"
    ):
        raise LeanProfileError("checkpoint policy differs")
    return dict(profile)


def classify_checkpoint_issue(
    issue_kind: str,
    *,
    provider_action_known: bool,
    repair_batches_used: int,
    safe_fallback_available: bool,
) -> CheckpointDecision:
    """Route a checkpoint issue without turning known operational failures into science STOPs."""

    load_lean_profile()
    if type(repair_batches_used) is not int or repair_batches_used < 0:
        raise LeanProfileError("repair_batches_used must be a non-negative integer")
    if type(provider_action_known) is not bool or type(safe_fallback_available) is not bool:
        raise LeanProfileError("checkpoint flags must be booleans")

    if issue_kind in OWNER_DECISION_ISSUE_KINDS:
        return CheckpointDecision.STOP_FOR_OWNER
    if issue_kind not in OPERATIONAL_ISSUE_KINDS:
        raise LeanProfileError("unknown checkpoint issue kind")
    if not provider_action_known:
        return CheckpointDecision.STOP_FOR_OWNER
    if repair_batches_used < 1:
        return CheckpointDecision.REPAIR_WITHIN_CHECKPOINT
    if safe_fallback_available:
        return CheckpointDecision.RECORD_AND_CONTINUE_WITH_FALLBACK
    return CheckpointDecision.CLOSE_CHECKPOINT_OPERATIONAL_STOP


def _identifier(value: Any, label: str) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise LeanProfileError(f"{label} is not a bounded identifier")
    return value


def _sha256(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise LeanProfileError(f"{label} is not a lowercase SHA-256")
    return value


def _decimal(value: Any, label: str) -> Decimal:
    if type(value) is not str or _DECIMAL.fullmatch(value) is None:
        raise LeanProfileError(f"{label} must be a non-negative decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise LeanProfileError(f"{label} is invalid") from error
    if not parsed.is_finite() or parsed < 0:
        raise LeanProfileError(f"{label} is invalid")
    return parsed


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _recorded_at(value: Any) -> str:
    if (
        type(value) is not str
        or not value
        or len(value) > 64
        or any(ord(char) > 127 for char in value)
    ):
        raise LeanProfileError("recorded_at must be bounded non-empty ASCII")
    return value


def _validate_row(row: Any, expected_sequence: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise LeanProfileError("attempt row must be an object")
    if row.get("schema_version") != "research-os-lean-attempt-event-v1":
        raise LeanProfileError("attempt row schema differs")
    if row.get("sequence") != expected_sequence or type(row.get("sequence")) is not int:
        raise LeanProfileError("attempt sequence is not contiguous")
    event = row.get("event")
    common = {"schema_version", "sequence", "event", "attempt_id", "request_sha256", "recorded_at"}
    _identifier(row.get("attempt_id"), "attempt_id")
    _sha256(row.get("request_sha256"), "request_sha256")
    _recorded_at(row.get("recorded_at"))

    if event == "INTENT":
        _exact_mapping(row, common | {"reserved_cost_usd"}, "intent row")
        _decimal(row["reserved_cost_usd"], "reserved_cost_usd")
        return row
    if event != "TERMINAL":
        raise LeanProfileError("attempt event is unknown")

    _exact_mapping(
        row,
        common
        | {
            "outcome",
            "provider_contacted",
            "raw_response_sha256",
            "observed_cost_usd",
            "included",
            "exclusion_reason",
        },
        "terminal row",
    )
    if row["outcome"] not in _OUTCOMES:
        raise LeanProfileError("terminal outcome is unknown")
    if row["provider_contacted"] is not None and type(row["provider_contacted"]) is not bool:
        raise LeanProfileError("provider_contacted must be true, false, or null")
    raw_sha = _sha256(row["raw_response_sha256"], "raw_response_sha256", nullable=True)
    _decimal(row["observed_cost_usd"], "observed_cost_usd")
    if type(row["included"]) is not bool:
        raise LeanProfileError("included must be a boolean")
    reason = row["exclusion_reason"]
    if reason is not None and (type(reason) is not str or not reason or len(reason) > 512):
        raise LeanProfileError("exclusion_reason must be null or bounded text")
    if row["included"] and (row["outcome"] != "SUCCESS" or reason is not None):
        raise LeanProfileError("only a successful terminal without an exclusion may be included")
    if row["included"] and raw_sha is None:
        raise LeanProfileError(
            "included success requires raw response identity, including local work"
        )
    if not row["included"] and reason is None:
        raise LeanProfileError("excluded terminal requires a reason")
    if row["provider_contacted"] is True and raw_sha is None:
        raise LeanProfileError("provider contact requires raw response identity")
    if (row["outcome"] == "UNKNOWN_EXTERNAL_OUTCOME") != (row["provider_contacted"] is None):
        raise LeanProfileError("unknown external outcome and provider status disagree")
    return row


def _decode_log(text: str) -> list[dict[str, Any]]:
    if text and not text.endswith("\n"):
        raise LeanProfileError("attempt log has an incomplete final row")
    rows: list[dict[str, Any]] = []
    for sequence, line in enumerate(text.splitlines(), start=1):
        try:
            decoded = json.loads(line)
        except json.JSONDecodeError as error:
            raise LeanProfileError("attempt log contains invalid JSON") from error
        rows.append(_validate_row(decoded, sequence))

    intents: dict[str, dict[str, Any]] = {}
    terminals: set[str] = set()
    for row in rows:
        attempt_id = row["attempt_id"]
        if row["event"] == "INTENT":
            if attempt_id in intents:
                raise LeanProfileError("attempt has duplicate intent")
            intents[attempt_id] = row
        else:
            if attempt_id not in intents:
                raise LeanProfileError("terminal has no prior intent")
            if attempt_id in terminals:
                raise LeanProfileError("attempt has duplicate terminal")
            if row["request_sha256"] != intents[attempt_id]["request_sha256"]:
                raise LeanProfileError("terminal request identity differs from intent")
            terminals.add(attempt_id)
    return rows


def _locked_append(
    path: Path, row_builder: Callable[[list[dict[str, Any]]], dict[str, Any]]
) -> dict[str, Any]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise LeanProfileError("attempt log cannot be opened safely") from error
    with os.fdopen(descriptor, "r+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        rows = _decode_log(handle.read())
        row = row_builder(rows)
        _validate_row(row, len(rows) + 1)
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        return dict(row)


def read_attempt_log(path: Path) -> tuple[dict[str, Any], ...]:
    """Read and validate a lean attempt JSONL without changing it."""

    path = Path(path)
    if not path.exists():
        return ()
    try:
        with path.open("r", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
            rows = _decode_log(handle.read())
    except OSError as error:
        raise LeanProfileError("attempt log cannot be read") from error
    return tuple(dict(row) for row in rows)


def append_attempt_intent(
    path: Path,
    *,
    attempt_id: str,
    request_sha256: str,
    reserved_cost_usd: str,
    budget_cap_usd: str,
    recorded_at: str,
) -> dict[str, Any]:
    """Atomically admit and reserve an attempt against this log's cumulative exposure cap.

    All writers must use the same approved cap and log. Dispatch only after this returns.
    """

    _identifier(attempt_id, "attempt_id")
    _sha256(request_sha256, "request_sha256")
    proposed = _decimal(reserved_cost_usd, "reserved_cost_usd")
    cap = _decimal(budget_cap_usd, "budget_cap_usd")
    _recorded_at(recorded_at)

    def build(rows: list[dict[str, Any]]) -> dict[str, Any]:
        if any(row["attempt_id"] == attempt_id for row in rows):
            raise LeanProfileError("attempt identity was already used")
        observed, outstanding = _exposure(rows)
        if observed + outstanding + proposed > cap:
            raise LeanProfileError("attempt reservation exceeds the cumulative budget cap")
        return {
            "schema_version": "research-os-lean-attempt-event-v1",
            "sequence": len(rows) + 1,
            "event": "INTENT",
            "attempt_id": attempt_id,
            "request_sha256": request_sha256,
            "reserved_cost_usd": reserved_cost_usd,
            "recorded_at": recorded_at,
        }

    return _locked_append(path, build)


def append_attempt_terminal(
    path: Path,
    *,
    attempt_id: str,
    request_sha256: str,
    outcome: str,
    provider_contacted: bool | None,
    raw_response_sha256: str | None,
    observed_cost_usd: str,
    included: bool,
    exclusion_reason: str | None,
    recorded_at: str,
) -> dict[str, Any]:
    """Append the only allowed terminal for a previously recorded attempt intent."""

    def build(rows: list[dict[str, Any]]) -> dict[str, Any]:
        intents = [
            row for row in rows if row["event"] == "INTENT" and row["attempt_id"] == attempt_id
        ]
        terminals = [
            row for row in rows if row["event"] == "TERMINAL" and row["attempt_id"] == attempt_id
        ]
        if len(intents) != 1:
            raise LeanProfileError("terminal requires exactly one prior intent")
        if terminals:
            raise LeanProfileError("attempt already has a terminal")
        if intents[0]["request_sha256"] != request_sha256:
            raise LeanProfileError("terminal request identity differs from intent")
        return {
            "schema_version": "research-os-lean-attempt-event-v1",
            "sequence": len(rows) + 1,
            "event": "TERMINAL",
            "attempt_id": attempt_id,
            "request_sha256": request_sha256,
            "outcome": outcome,
            "provider_contacted": provider_contacted,
            "raw_response_sha256": raw_response_sha256,
            "observed_cost_usd": observed_cost_usd,
            "included": included,
            "exclusion_reason": exclusion_reason,
            "recorded_at": recorded_at,
        }

    return _locked_append(path, build)


def budget_allows(
    *, cap_usd: str, observed_usd: str, outstanding_reserved_usd: str, proposed_max_usd: str
) -> bool:
    """Advisory arithmetic only; use append_attempt_intent for atomic admission."""

    return _decimal(observed_usd, "observed_usd") + _decimal(
        outstanding_reserved_usd, "outstanding_reserved_usd"
    ) + _decimal(proposed_max_usd, "proposed_max_usd") <= _decimal(cap_usd, "cap_usd")


def _exposure(rows: Iterable[dict[str, Any]]) -> tuple[Decimal, Decimal]:
    intents = {}
    terminals = {}
    for row in rows:
        (intents if row["event"] == "INTENT" else terminals)[row["attempt_id"]] = row
    observed = Decimal(0)
    outstanding = Decimal(0)
    for attempt_id, intent in intents.items():
        reserved = _decimal(intent["reserved_cost_usd"], "reserved_cost_usd")
        terminal = terminals.get(attempt_id)
        if terminal is None:
            outstanding += reserved
            continue
        cost = _decimal(terminal["observed_cost_usd"], "observed_cost_usd")
        observed += cost
        if terminal["outcome"] == "UNKNOWN_EXTERNAL_OUTCOME":
            # Known charges are part of, not additional to, the reserved maximum.
            outstanding += max(reserved - cost, Decimal(0))
    return observed, outstanding


def reconcile_attempts(
    path: Path, *, planned_attempt_ids: Iterable[str], budget_cap_usd: str
) -> dict[str, Any]:
    """Reconcile the planned dataset, terminal coverage, reservations and observed spend."""

    planned = list(planned_attempt_ids)
    if not planned:
        raise LeanProfileError("planned attempt identities must not be empty")
    if len(planned) != len(set(planned)):
        raise LeanProfileError("planned attempt identities are duplicated")
    for attempt_id in planned:
        _identifier(attempt_id, "planned attempt_id")
    planned_set = set(planned)
    cap = _decimal(budget_cap_usd, "budget_cap_usd")
    rows = read_attempt_log(path)
    intents = {row["attempt_id"]: row for row in rows if row["event"] == "INTENT"}
    terminals = {row["attempt_id"]: row for row in rows if row["event"] == "TERMINAL"}
    unknown_ids = (set(intents) | set(terminals)) - planned_set
    if unknown_ids:
        raise LeanProfileError("attempt log contains an unplanned identity")

    spend, outstanding = _exposure(rows)
    reservation_exceeded = sorted(
        attempt_id
        for attempt_id, terminal in terminals.items()
        if _decimal(terminal["observed_cost_usd"], "observed_cost_usd")
        > _decimal(intents[attempt_id]["reserved_cost_usd"], "reserved_cost_usd")
    )
    missing = sorted(planned_set - set(terminals))
    ambiguous = sorted(
        attempt_id
        for attempt_id, row in terminals.items()
        if row["outcome"] == "UNKNOWN_EXTERNAL_OUTCOME"
    )
    included_count = sum(row["included"] for row in terminals.values())
    dataset_complete = not missing
    within_budget = spend <= cap
    projected_within_budget = spend + outstanding <= cap
    analysis_ready = (
        dataset_complete and not ambiguous and not reservation_exceeded and within_budget
    )
    return {
        "schema_version": "research-os-lean-reconciliation-v1",
        "planned_attempts": len(planned),
        "intent_count": len(intents),
        "terminal_count": len(terminals),
        "included_count": included_count,
        "excluded_count": len(terminals) - included_count,
        "missing_attempt_ids": missing,
        "ambiguous_attempt_ids": ambiguous,
        "reservation_exceeded_attempt_ids": reservation_exceeded,
        "observed_spend_usd": _decimal_text(spend),
        "outstanding_reserved_usd": _decimal_text(outstanding),
        "budget_cap_usd": _decimal_text(cap),
        "within_budget": within_budget,
        "projected_within_budget": projected_within_budget,
        "dataset_complete": dataset_complete,
        "analysis_ready": analysis_ready,
    }


__all__ = [
    "CheckpointDecision",
    "LeanProfileError",
    "append_attempt_intent",
    "append_attempt_terminal",
    "budget_allows",
    "classify_checkpoint_issue",
    "load_lean_profile",
    "read_attempt_log",
    "reconcile_attempts",
]
