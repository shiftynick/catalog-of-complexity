---
name: scout-systems
description: Discover candidate complex systems worth cataloging and the metrics that would characterize them. Produces proposal tasks that `profile-system`, `define-metrics`, and `extract-observations` consume — this skill does not write canonical records directly.
status: active
inputs:
  - 'topic — free-text scope seed (e.g. "gut microbiome", "high-voltage power grids", "stock market microstructure").'
  - 'budget — integer. Maximum number of candidate systems to surface in this run (default 3). Keep this small: each candidate becomes a profile-system task, and a 5-candidate scout monopolizes downstream runs with a single domain for ~5 iterations before cross-domain rotation can resume. plan-backlog overrides to 2 when fanning out across multiple under-covered domains.'
  - 'domain_hint — optional taxonomy slug (`system-domain:ecological`, etc.) to constrain the search.'
outputs:
  - 'One `ops/tasks/inbox/tsk-YYYYMMDD-NNNNNN.yaml` per candidate system (type `profile-system`).'
  - 'Zero or more `ops/tasks/inbox/` tasks for candidate metrics not yet in the registry (type `define-metrics`).'
  - 'A scouting report at `ops/runs/YYYY/MM/DD/<run-id>/scout-report.md` summarising rejected candidates and rationale.'
stop_conditions:
  - '`budget` candidate profile-system tasks queued in inbox with at least one candidate source cited per system.'
  - 'Fewer than `budget` candidates found after an exhaustive pass — record the shortfall in the scout report and proceed.'
  - 'No taxonomy slug covers a candidate system — block with a `taxonomy-proposal` task rather than inventing a slug.'
---

## When to use

Use this skill to widen the catalog's coverage. Typical triggers:

- A domain is underrepresented in the system roster (`v_coverage_by_family` shows thin columns).
- A metric family has fewer than N observations across systems.
- A reviewer has identified a literature thread worth following.

Do **not** use this skill to finalize system definitions or extract measurements — it only proposes.

## Preconditions

- The task manifest supplies `topic` (required) and `budget` (optional, default 3). Read the manifest's `notes` field for an explicit budget override (e.g. "Budget: 2 candidate systems").
- Taxonomy exports are current — if `taxonomy/exports/labels.json` is missing or stale, run `uv run coc export-taxonomy` first.

## Procedure

1. Read the current system roster: `registry/systems/*/system.yaml` (just the `name`, `slug`, and `taxonomy_refs` fields) to avoid duplicate proposals.
2. Read the taxonomy exports at [labels.json](../../taxonomy/exports/labels.json) to know the available `system-domain` and `system-class` slugs.
3. Search the literature for systems matching `topic`. Prefer review articles and handbooks over primary research when scouting breadth.
4. For each candidate system:
   - Draft a 1-paragraph description of its boundary and components.
   - Pick one `system-domain` and one or more `system-class` slugs. If no slug fits, queue a `taxonomy-proposal` task instead of inventing.
   - Identify at least one citable source (DOI, handbook chapter, canonical review).
   - Identify 2-5 candidate metrics that would characterize this system. For each, check whether the metric already exists in `registry/metrics/`. If not, add it to the candidate-metrics list for this run.
5. Emit one `profile-system` task per candidate into `ops/tasks/inbox/` with `system_id: null` (the profile-system skill will assign the ID), the proposed slug in `notes`, and the candidate source(s) in `source_refs`.
6. Emit one `define-metrics` task per novel candidate metric into `ops/tasks/inbox/`.
7. Write the scout report listing each accepted candidate, each rejected candidate with rationale, and any taxonomy gaps.
8. Validate the new task files: `uv run coc validate ops/tasks/inbox/`.

## Output shape

- `ops/tasks/inbox/tsk-*.yaml` — each valid against [task.schema.json](../../schemas/task.schema.json), `state: inbox`.
- `ops/runs/.../scout-report.md` — markdown with sections: Accepted, Rejected, Taxonomy gaps, Sources consulted.

## Block or fail when

- Candidate volume exceeds `budget` × 3 — the topic is too broad; block with a narrower-topic proposal.
- All candidates were rejected (no viable systems) — block with `state: blocked`, reason = no-candidates-found.
- Any candidate's sources are exclusively behind paywalls we can't archive — note in the scout report but do not block (sources can be stubbed at `source-status: pending-acquisition`).

## References

- [taxonomy/source/system-domains.yaml](../../taxonomy/source/system-domains.yaml)
- [taxonomy/source/system-classes.yaml](../../taxonomy/source/system-classes.yaml)
- [taxonomy/source/metric-families.yaml](../../taxonomy/source/metric-families.yaml)
- [schemas/task.schema.json](../../schemas/task.schema.json)
