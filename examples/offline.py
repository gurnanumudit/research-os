"""Network-free synthetic example; no credentials, provider calls, or retained study files."""

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from evals_to_outcomes.research_os_lean import (
    append_attempt_intent,
    append_attempt_terminal,
    reconcile_attempts,
)


def main() -> None:
    request = b"Synthetic offline check: 2 + 2"
    output = b"4"
    with TemporaryDirectory(prefix="research-os-example-") as directory:
        log = Path(directory) / "attempts.jsonl"
        request_hash = hashlib.sha256(request).hexdigest()
        append_attempt_intent(
            log,
            attempt_id="offline-1",
            request_sha256=request_hash,
            reserved_cost_usd="0",
            budget_cap_usd="0",
            recorded_at="2026-09-13T00:00:00Z",
        )
        append_attempt_terminal(
            log,
            attempt_id="offline-1",
            request_sha256=request_hash,
            outcome="SUCCESS",
            provider_contacted=False,
            raw_response_sha256=hashlib.sha256(output).hexdigest(),
            observed_cost_usd="0",
            included=True,
            exclusion_reason=None,
            recorded_at="2026-09-13T00:00:01Z",
        )
        print(
            json.dumps(
                reconcile_attempts(log, planned_attempt_ids=["offline-1"], budget_cap_usd="0"),
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
