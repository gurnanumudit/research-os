# Research OS

Research OS is a small set of controls for running trustworthy AI studies without turning every
experiment into an infrastructure project.

The current release, `lean-default-v1`, keeps the scientific essentials strict:

- freeze the protocol before observing outcomes;
- keep labels hidden from generators and verifiers;
- preserve one intent and one terminal record for every attempt;
- enforce the approved budget;
- reconcile missing, included, and excluded observations; and
- make the final analysis reproducible.

Operational failures normally get one bounded repair. They stop a study only when continuing would
change the science, exceed owner authority, lose evidence, or make an external action ambiguous.

## What is included

- a versioned lean-default profile;
- checkpoint issue classification;
- an append-only attempt ledger;
- budget admission and reconciliation;
- dataset-completeness checks;
- a focused test suite; and
- the operating principles and design rationale.

## What is not included

This repository intentionally excludes provider credentials, private study data, historical study
artifacts, website code, and bespoke execution machinery. A real study still supplies its frozen
protocol, study-specific scorer or assay, and a thin provider adapter.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

## Status

`lean-default-v1` is tested and ready to integrate into a prospective study. It is a reusable
research control layer, not a hosted experiment runner.

See [the operating principles](docs/operating-principles.md) and
[the lean-default design](docs/lean-default-design.md).
