# Research OS

Research OS is a small set of controls for running trustworthy AI studies without turning every
experiment into an infrastructure project.

The `lean-default-v1` profile names the scientific essentials a study should protect:

- freeze the protocol before observing outcomes;
- keep labels hidden from generators and verifiers;
- preserve one intent and one terminal record for every attempt;
- respect the approved budget;
- reconcile missing, included, and excluded observations; and
- make the final analysis reproducible.

The supplied checkpoint policy allows one bounded repair. It recommends stopping when continuing would
change the science, exceed owner authority, lose evidence, or make an external action ambiguous.

## What is included

- a versioned lean-default profile;
- checkpoint issue classification;
- an append-only attempt ledger;
- lock-protected budget admission and reconciliation;
- dataset-completeness checks;
- a focused test suite; and
- the operating principles and design rationale.

## What is not included

This repository excludes provider credentials, private study data, historical study artifacts,
website code, and execution machinery. It does **not** enforce protocol freezing, label blinding,
scorer validity, time limits, or external dispatch. A real study supplies those controls, its raw
evidence store, and its provider adapter. A hash is an evidence reference, not verification that the
referenced bytes exist or are scientifically valid.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
python examples/offline.py
```

The example uses a temporary local ledger and synthetic evidence, makes no network/provider calls,
and leaves no study files behind. See [integration and limits](docs/lean-default-design.md).

## Status

Version 0.1.1 is an early, reusable control library, not a hosted runner or an end-to-end scientific
assurance system. Python 3.11+ on Linux/macOS is supported; the file-lock implementation requires
POSIX `fcntl`, so Windows is not supported. Use one local filesystem ledger and one approved cap
across all cooperating writers. Network filesystems, adversarial log tampering, exactly-once remote
dispatch, and automatic crash recovery are not supported. Incomplete writes fail closed.

The admission API requires `budget_cap_usd` on `append_attempt_intent`; `budget_allows` requires
`outstanding_reserved_usd`. This is an intentional pre-1.0 API correction. Callers must migrate
both arguments and dispatch only after the atomic intent append succeeds.

Research OS grew out of the [AI product research program](https://github.com/gurnanumudit/ai-product-research).
The [research site](https://research.muditgurnani.chatgpt.site) presents the broader work; this does
not imply that every historical study used this exact library. This standalone extraction includes
neither the historical CP3 runtime nor Track A/B validators. Profile entries for optional
high-assurance controls are descriptive policy names, not bundled implementations.

Licensed under the [MIT License](LICENSE).

See [the operating principles](docs/operating-principles.md) and
[the lean-default design](docs/lean-default-design.md).
