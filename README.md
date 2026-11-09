# Independent Therapeutics ResearchOS Concept

An independent offline research prototype for evidence traceability, declared study
context, version-bound human review, descriptive assay summaries and ResearchOS replay.
Not affiliated with, sponsored by or endorsed by United Therapeutics. No company
systems or proprietary data are connected. The repository name identifies a concept,
not an established partnership.

## Install and run

Python 3.10 or later; standard-library runtime, no account or paid service needed.

```bash
python -m pip install .
mkdir -p runs
therapeutics-research analyze examples/dossier.json --output runs/example
therapeutics-research verify runs/example
python -m unittest discover -s tests -v
python tests/check_installed.py
```

Open `runs/example/review.html` for evidence blockers, captured declarations, assay
summary and ResearchOS state. Without installing, use `python -m therapeutics_research`.
Outputs must be new directories with existing parents. Exit 0 means scoped analysis
or exact historical replay succeeded, including correctly recorded blocked claims.
It does not mean scientific validation or ASSURED status. Invalid inputs, stale review
bindings, existing outputs and changed bundles return exit 2.

The example uses fictional assay values and no human-review declarations. Its claim
therefore remains UNVERIFIED. Its fixed assessment and expiry dates describe a captured
example; new studies must supply their own dates. Replay never renews evidence validity.

## Implemented checks

| Component | Scope |
| --- | --- |
| Evidence bytes | Strict base64, SHA-256 comparison, byte bounds, source identifier |
| Context | Exact declared species, model, endpoint and unit matching |
| Validity | Explicit observation/expiry interval at captured assessment time |
| Claims | Versions, statements, evidence references and acyclic dependencies |
| Human review | Explicit accept/revise/reject, reviewer declaration, reasons and version/evidence binding |
| Change impact | Review bindings include transitive upstream claim and evidence declarations |
| Assay summary | Strict two-group replicate CSV; count, mean, sample variance and descriptive mean difference |
| ResearchOS | Canonical evidence receipts, dependency transitions, blockers and replay ledger |

Digest/context/validity failures stay visible and prevent local support. Assay summaries
are blocked when their raw-data artifact fails those checks. Malformed input or malformed
assay CSV is rejected. No evidence text is interpreted as scientific proof.

## Input contract

See [examples/dossier.json](examples/dossier.json). Required fields are `schema_version`,
`label`, `as_of`, `expires_at`, `context`, `claims`, `artifacts`, `reviews`, `assay`.
`assay` may be null. Claims reference captured artifact IDs. Artifact kinds are protocol,
raw_data, analysis, literature or replication; a replication label does not establish
independence or satisfy ResearchOS reproduction gates.

Artifacts contain actual base64 bytes and their declared SHA-256, source ID, context,
observation time and expiry. Limits: 32 claims, 64 artifacts, 64 KiB per artifact,
1 MiB total decoded evidence, 128 review records and 8 MiB input/output files.
Unknown fields, duplicate JSON keys, nonfinite values and invalid timestamps are rejected.
Input is not a clinical-record schema; do not include identifiable patient information.

Optional assay CSV has exactly `replicate_id,group,value`, with distinct replicate IDs,
two explicitly named groups, finite numeric values bounded by magnitude 1e12 and at
most 10000 rows. Each group requires at least one observation. Sample variance is
null for a single observation. Units come from the declared context; no conversion or
normalization occurs. Equal units do not make different biological models comparable.
The tool does not fit a dose response, test significance or estimate therapeutic effects.

## Review and revalidation

Each review specifies ID, claim ID/version, `evidence_binding`, reviewer ID,
decision, reason and review time. Compute the binding using
`therapeutics_research.dossier.evidence_binding(claim, artifacts_by_id, claims_by_id)`
on the complete current dossier. The report exposes each current binding for inspection.
Bindings cover the claim statement/version, all referenced artifact declarations and
transitive prerequisite declarations. Changed inputs invalidate prior bindings.

Only one current review per claim is accepted in this snapshot format. Review time must
follow all directly referenced observations and not exceed assessment time. Supplied
reviewer identity and source metadata are not authenticated. An accept decision cannot
override failed integrity, mismatched context, expired evidence or blocked prerequisites.
Review acceptance establishes declared workflow satisfaction, not biomedical correctness.

## ResearchOS integration and bundles

Six unchanged canonical v0.1.0 modules are pinned in
[researchos-lock.json](researchos-lock.json). Conformance tests verify release hashes.
The adapter calls the real Controller and maps prerequisite-to-dependent relations.
It records receipts for local dossier checks. Review-required claims receive UNCERTAIN
evidence; supported declarations may reach ADVERSARIAL_TEST. Missing domain attacks
and separate reproduction prevent further promotion. No fictional expert or reproduction
records are supplied by the implementation.

Confidence, density threshold .001 and evidence weights are explicit local policy,
not calibrated scientific trust. Every reconstructed controller begins claim version 1;
actual domain versions and evidence bindings remain in captured receipts. This is an
offline snapshot workflow, not a persistent clinical system or shared review platform.

Bundles contain captured input, dossier results, scenario, ledger, controller report,
escaped HTML and runtime/content hashes. Verify recomputes every byte, including
assay statistics and controller operations. It does not authenticate sources or prove
replicate independence. Anyone who changes the input can create a different consistent
study. Historical replay uses captured time and exact implementation behavior; it is
not a present-day evidence-freshness check.

## Limits and development

No efficacy, safety, dosing, diagnosis, treatment, transplant-allocation or equipment
decision is authorized. No clinical trial, regulatory approval, compliance certification
or company collaboration is established. External source authentication, scientific
adjudication and independent reproduction remain outstanding. See
[research scope](docs/RESEARCH_SCOPE.md).

Tests cover hand-calculated summaries, review binding and upstream changes, evidence
integrity/context/expiry failures, malformed CSV, dependencies, role/digest/expiry
rejection, replay tampering and core conformance. Installed CLI tests import outside
the checkout. CI runs Python 3.10, 3.12 and 3.13 with fictional data only.
Existing Apache-2.0 license retained; canonical ResearchOs code is Apache-2.0.

**∞**
