# Research OS lean-default vNext

Date: 2026-09-10  
Status: implementation design; no study, provider, publication or deployment authority

## Outcome

Research OS remains one product and one codebase. The proven CP3 runtime is preserved byte-for-byte
as the `high-assurance` behavior. `lean-default-v1` is an additive, versioned profile in the same
package. A study selects the lean profile unless its risk assessment explicitly activates one or
more high-assurance modules.

This design implements the operating principle already recorded in
[`operating-principles.md`](operating-principles.md): protect scientific
validity, but do not confuse engineering ceremony with rigor.

## Lean lifecycle

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

## Profile boundary

The lean profile is configuration plus small reusable primitives. It does not duplicate Track A or
Track B:

- Track A remains the source of truth for construct, data and sample-plan validation.
- Track B remains the source of truth for scorer, assay and oracle-boundary validation.
- The lean profile supplies checkpoint issue classification, one-repair/fallback policy, a compact
  append-only attempt ledger, budget reconciliation and dataset-completeness checks.
- Existing CP3 `govern(case_id)` and all frozen reports remain unchanged.

High-assurance modules stay available but default off: transition-by-transition audit, immutable
permissions for every intermediate, multiple GO receipt files, exhaustive injected-fault suites,
full crash/custody ceremony and root-only release files.

## Migration

1. Add the `lean-default-v1` profile resource and lean primitives/tests to the main
   `evals_to_outcomes` package. Do not add files inside the preserved CP3 directory: its exact
   implementation manifest intentionally rejects unlisted files, so an in-place extension would
   invalidate the high-assurance runtime rather than create a safe profile.
2. Run the lean-profile tests and the entire preserved CP3 suite. Existing CP3 bytes and behavior
   must not change.
3. On the next prospective study—not the active Study 1—bind its frozen protocol to
   `lean-default-v1` and use a small provider adapter.
4. Measure overhead, repair use, fallback use and time-to-first-scientific-observation.
5. After the study, promote only observed, conclusion-relevant failures into new default controls.

No active Study 1 artifact is migrated or rewritten. Its records remain the evidence that motivated
this change.
