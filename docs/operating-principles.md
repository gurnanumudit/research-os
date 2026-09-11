# Research OS operating principles

Recorded: 2026-09-09  
Status: Core operating principle for prospective Research OS and study work

## Core principle

Research OS exists to make scientific learning trustworthy **and faster**. It must protect
scientific validity without confusing engineering ceremony with scientific rigor.

The default workflow is:

> **Run, learn, disclose, improve.**

Controls are proportional and iterative. Early studies may have limitations; those limitations
must be recorded honestly rather than hidden behind process or treated as a reason to perfect the
infrastructure before learning anything.

## What remains non-negotiable

Research OS must protect the few conditions that can materially change or invalidate a result:

- freeze the research question, comparison, sample rule, metrics, stopping rule, and claim boundary
  before outcome-informed analysis;
- prevent private labels or outcome truth from leaking into blinded stages;
- preserve the raw requests, responses, executions, and labels needed to reconstruct the reported
  result;
- prevent undisclosed duplicate observations and material deviations from the frozen design;
- enforce approved cost, privacy, security, credential, and external-action boundaries; and
- report exclusions, missing evidence, deviations, uncertainty, and study limitations plainly.

These are scientific-integrity and owner-authority safeguards. They may block a run when safe
continuation cannot preserve a trustworthy conclusion.

## What should normally warn, repair, and continue

The following are operational problems, not automatic scientific failures, when they occur before
outcome leakage and can be repaired without changing the study:

- unavailable or expired credentials before provider contact;
- network, provider, or environment setup failures;
- formatting, schema, metadata, naming, inventory, or hash-shape defects that do not compromise the
  underlying raw evidence;
- recoverable crashes for which dispatch status is known;
- invalid, incomplete, or truncated assay candidates that can be repaired under the frozen rules;
- missing nonessential documentation; and
- ordinary implementation defects that leave the scientific design and evidence unchanged.

These events should be logged, corrected, and retried within the approved budget and time box. A
single candidate or recoverable setup failure should not stop the whole study.

## Blocking standard

Research OS blocks only when continuing would create a meaningful risk of:

1. an invalid or outcome-informed scientific conclusion;
2. unknown, corrupted, substituted, or irrecoverable result evidence;
3. an outcome-affecting duplicate or an execution whose occurrence cannot be determined;
4. an unauthorized cost, privacy, security, credential, or external action; or
5. running a materially different experiment while presenting it as the frozen one.

Everything else defaults to **warn, log, repair, and continue**.

## How controls evolve

A new blocking control is justified only when all three questions have satisfactory answers:

1. What concrete failure have we observed or have strong evidence will occur?
2. Could it materially change the scientific conclusion or violate an owner boundary?
3. Is this the simplest, lowest-friction control that addresses it?

Speculative edge cases do not become blocking gates by default. Audits are batched at meaningful
study checkpoints rather than repeated for every file or internal transition. A new version is
required for a material change to the scientific design, data, models, scoring, or claim—not for
every operational retry.

Research OS overhead should normally remain below 15% of total study effort. When it exceeds that
level, the default response is to simplify or remove controls, not to extend the engineering phase.
Controls are reviewed after each study and improved prospectively from observed failures.

## Publication standard

Credibility comes from a clear question, appropriate evidence, reproducible core results, bounded
claims, and honest limitations. A paper does not need maximum possible procedural rigor. It must
state what was tested, what happened, what remains uncertain, and what changed during execution.

This principle governs future Research OS changes and study configurations. Historical artifacts
remain preserved as evidence of how the operating approach evolved.
