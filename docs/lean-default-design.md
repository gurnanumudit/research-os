# Research OS lean-default integration

Updated: 2026-09-13

Scope: standalone library; no study or provider authority is granted by installing it.

## Outcome

This repository publishes the `lean-default-v1` policy resource and small Python primitives. It was
extracted from a broader research workspace; that workspace's CP3 runtime and Track A/B validators
are not included here. Optional high-assurance names in the profile describe possible additional
study controls, not modules this package implements.

This design implements the operating principle already recorded in
[`operating-principles.md`](operating-principles.md): protect scientific
validity, but do not confuse engineering ceremony with rigor.

## Lean lifecycle

This is a recommended study workflow, not a lifecycle automatically enforced by this library.

1. **Freeze science once.** Record the question, estimands, comparison, data identities, exclusions,
   sample/stopping rule, metrics, scorer version, budget cap and claim boundary.
2. **Qualify the real boundary once.** Run a network-free adapter smoke test, then a minimal
   production-shaped capability canary before consuming scientific identities. A mock cannot prove
   authentication, provider schemas, remote packages or runtime executables.
3. **Execute through one attempt log.** Each unique attempt has one intent and one terminal. The
   terminal binds raw response identity, observed cost, inclusion/exclusion status and any deviation.
4. **Seal predictions before labels.** Blinded stages cannot read outcome truth. Labels open only
   after the prediction/candidate panel is sealed.
5. **Reconcile completeness and budget.** Planned = terminal + prospectively excluded + explicitly
   missing. There are no silent rows, duplicate attempts or unexplained spend.
6. **Reproduce analysis.** One command rebuilds the reported tables and estimates from sealed inputs.
   An independent review happens at the checkpoint boundary, not after every internal file write.

## Checkpoint decisions

The default maximum is **one bounded repair batch per checkpoint**.

| Situation | Default action |
| --- | --- |
| Missing/expired credential before provider contact; local transport/import failure; provider schema mismatch; environment/package/runtime problem; formatting or metadata defect | Record the incident and repair inside the same checkpoint, provided provider-action status is known and science, cost and security boundaries do not change. |
| The bounded repair is exhausted and a prospectively allowed fallback exists | Record the failed path, activate the fallback, and continue. Do not create another wrapper or operational version. |
| The bounded repair is exhausted and no safe fallback exists | Close the checkpoint as an operational STOP with exact evidence. This is not automatically a request to redesign the study. |
| Research question, estimand, sample/selection rule, model condition, scorer, claim boundary or outcome interpretation must change | Stop for owner decision and create a prospective scientific amendment/version if approved. |
| New paid cost, privacy/security boundary change, external action, or unknown/ambiguous provider dispatch | Stop for owner decision. An ambiguous external attempt consumes its identity and is never retried. |

`record-and-continue` never means hide a problem. The incident, affected attempts, fallback and
effect on the analysis remain in the final limitations and completeness report.

## Loop prevention

- One scientific objective and one executable acceptance statement per checkpoint.
- One canonical runtime and attempt ledger; no parallel trees of release receipts.
- One batched repair allowance. If the same failure signature remains, use the frozen fallback or
  close the checkpoint—do not add a new control layer.
- Allocate checkpoint time to build, adversarial review and live contingency. Track
  time-to-first-scientific-observation alongside test counts.
- A new Research OS profile/version is justified by a changed scientific or authority boundary,
  not by an ordinary pre-dispatch code fix.
- Keep Research OS overhead below the existing 15% target. If it exceeds the target, simplify the
  controls before extending the engineering phase.

## Integrating the API

Use `append_attempt_intent` with the approved `budget_cap_usd` before dispatch. It checks settled
spend plus outstanding exposure plus the proposed reservation while holding the same file lock
used for the durable append. All writers must use the same ledger and cap; the library cannot
authenticate owner approval or prevent a caller from bypassing it. `budget_allows` is advisory
arithmetic, not a transaction: it must not replace the locked admission call.

Record one terminal per intent. A known terminal treats `observed_cost_usd` as settled whole-attempt
cost; do not report it as known if billing or dispatch remains uncertain. For
`UNKNOWN_EXTERNAL_OUTCOME`, reconciliation retains the unobserved portion of the original
reservation: total exposure is at least the larger of reservation and observed charge, without
double-counting the observed portion. Ambiguous outcomes block analysis readiness. There is no
automatic settlement-amendment API or retry of an ambiguous identity; resolution needs separately
reviewed evidence and must not erase the predecessor log.

Every included success, including local-only work, requires a raw-output SHA-256 reference. The
caller must preserve and independently verify those bytes. `analysis_ready` means the planned
terminal rows are present, unambiguous, within budget and free of reservation overruns; it does not
validate labels, exclusions, inferential methods, hashes against files, or scientific conclusions.
Dataset completeness counts excluded terminals too, and is not an accuracy metric.

The ledger is append-only through this API, not immutable against filesystem owners. Locks require
cooperating writers on a local POSIX filesystem. A crash can leave a truncated line; reading then
fails closed, and this package deliberately does not guess or redo the external action. Use a
study-owned recovery procedure. No historical study artifacts are migrated by this release.
