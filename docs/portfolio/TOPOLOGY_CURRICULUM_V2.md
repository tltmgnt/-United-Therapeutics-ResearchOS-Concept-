# Topology compatibility and curriculum v2 — -United-Therapeutics-ResearchOS-Concept-

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | application research |
| Minimum useful mathematics | Acyclic claim dependencies and version-bound evidence graphs |
| Relationships to preserve | Declared species/model/endpoint/unit context and transitive review bindings |
| Concrete operation / capstone | Change the declared endpoint or upstream evidence and trace the resulting dossier blockers |
| Necessity and scope boundary | Assay differences are descriptive; no treatment effect, company affiliation or clinical authorization follows |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with acyclic claim dependencies and version-bound evidence graphs and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify declared species/model/endpoint/unit context and transitive review bindings. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain acyclic claim dependencies and version-bound evidence graphs. | Change the declared endpoint or upstream evidence and trace the resulting dossier blockers. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `1472a1435be7677cb26bdc020698cfa1e5b670d3` in [therapeutics_research/dossier.py](../../therapeutics_research/dossier.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [11](../../therapeutics_research/dossier.py#L11) | `def context(value):` | State the input/output contract and trace one normal and one failing case. |
| [16](../../therapeutics_research/dossier.py#L16) | `def identifiers(values, maximum):` | State the input/output contract and trace one normal and one failing case. |
| [17](../../therapeutics_research/dossier.py#L17) | `if type(values) is not list or len(values)>maximum: raise ValueError('Bounded identifier list required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [19](../../therapeutics_research/dossier.py#L19) | `if len(set(values))!=len(values): raise ValueError('Duplicate identifier')` | Construct the triggering input and explain why rejection preserves the contract. |
| [22](../../therapeutics_research/dossier.py#L22) | `def records(values, maximum):` | State the input/output contract and trace one normal and one failing case. |
| [23](../../therapeutics_research/dossier.py#L23) | `if type(values) is not list or not 1<=len(values)<=maximum: raise ValueError('Nonempty bounded records required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [26](../../therapeutics_research/dossier.py#L26) | `if type(value) is not dict: raise ValueError('Object records required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [28](../../therapeutics_research/dossier.py#L28) | `if identifier in result: raise ValueError('Duplicate record ID')` | Construct the triggering input and explain why rejection preserves the contract. |
| [30](../../therapeutics_research/dossier.py#L30) | `return result` | Predict the returned value and distinguish a computed result from authorization. |
| [33](../../therapeutics_research/dossier.py#L33) | `def evidence_binding(claim, artifacts, claims):` | State the input/output contract and trace one normal and one failing case. |
| [43](../../therapeutics_research/dossier.py#L43) | `return digest({'claim':claim,'artifacts':[artifacts[e] for e in sorted(claim['evidence_ids'])],` | Explain the exact bytes bound by the digest and why hashing does not authenticate the source. |
| [47](../../therapeutics_research/dossier.py#L47) | `def assay_summary(content, control, treatment):` | State the input/output contract and trace one normal and one failing case. |
| [49](../../therapeutics_research/dossier.py#L49) | `if control==treatment: raise ValueError('Two distinct assay groups required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [51](../../therapeutics_research/dossier.py#L51) | `if reader.fieldnames!=['replicate_id','group','value']: raise ValueError('Exact assay CSV columns required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [54](../../therapeutics_research/dossier.py#L54) | `if len(seen)>=10000 or None in row or any(v is None for v in row.values()): raise ValueError('Malformed or oversized assay')` | Construct the triggering input and explain why rejection preserves the contract. |
| [56](../../therapeutics_research/dossier.py#L56) | `if identifier in seen or group not in groups: raise ValueError('Duplicate replicate or unexpected group')` | Construct the triggering input and explain why rejection preserves the contract. |
| [58](../../therapeutics_research/dossier.py#L58) | `except (TypeError,ValueError) as exc: raise ValueError('Numeric assay value required') from exc` | Construct the triggering input and explain why rejection preserves the contract. |
| [59](../../therapeutics_research/dossier.py#L59) | `if not math.isfinite(value) or abs(value)>1e12: raise ValueError('Bounded finite assay value required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [61](../../therapeutics_research/dossier.py#L61) | `if any(not v for v in groups.values()): raise ValueError('Both assay groups require observations')` | Construct the triggering input and explain why rejection preserves the contract. |
| [63](../../therapeutics_research/dossier.py#L63) | `return {'groups':summary,'treatment_minus_control_mean':summary[treatment]['mean']-summary[control]['mean'],` | Predict the returned value and distinguish a computed result from authorization. |
| [67](../../therapeutics_research/dossier.py#L67) | `def evaluate(data):` | State the input/output contract and trace one normal and one failing case. |
| [68](../../therapeutics_research/dossier.py#L68) | `fields(data, ('schema_version','label','as_of','expires_at','context','claims','artifacts','reviews','assay'))` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [69](../../therapeutics_research/dossier.py#L69) | `if type(data['schema_version']) is not int or data['schema_version']!=1: raise ValueError('Unsupported schema')` | Construct the triggering input and explain why rejection preserves the contract. |
| [72](../../therapeutics_research/dossier.py#L72) | `if date(data['expires_at'])<=as_of: raise ValueError('Expiry must follow assessment time')` | Construct the triggering input and explain why rejection preserves the contract. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_dossier.py](../../tests/test_dossier.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. Assay differences are descriptive; no treatment effect, company affiliation or clinical authorization follows.
