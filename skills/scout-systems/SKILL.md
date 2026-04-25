---
name: scout-systems
description: Propose missing type-level complex-system archetypes against the priority list and existing taxonomy. Produces `profile-system` proposal tasks and (rarely) `review-records` taxonomy-proposal tasks. Does NOT search literature for specific case studies — the catalog holds types, not instances. See AGENTS.md "What counts as a system worth cataloging" for the inclusion criterion.
status: active
inputs:
  - 'topic — type-level archetype name (e.g. "metabolic network", "market", "language"). Should match or imply a `system-class` slug. Free-form case studies (e.g. "the 2008 financial crisis") are out of scope.'
  - 'budget — integer. Maximum number of candidate type-level systems to surface in this run (default 3). Keep this small: each candidate becomes a profile-system task. plan-backlog overrides to 2 when fanning out across multiple under-covered domains.'
  - 'domain_hint — optional taxonomy slug (`system-domain:ecological`, etc.) to constrain the search.'
outputs:
  - 'One `ops/tasks/inbox/tsk-YYYYMMDD-NNNNNN.yaml` per candidate type-level system (type `profile-system`).'
  - 'Zero or more `ops/tasks/inbox/` tasks proposing taxonomy slugs missing from `taxonomy/source/system-classes.yaml` (type `review-records`).'
  - 'A scouting report at `ops/runs/YYYY/MM/DD/<run-id>/scout-report.md` listing accepted and rejected candidates with rationale.'
stop_conditions:
  - '`budget` candidate type-level profile-system tasks queued in inbox.'
  - 'Fewer than `budget` candidates pass the inclusion criterion (AGENTS.md) after an exhaustive pass — record the shortfall in the scout report and proceed.'
  - 'No taxonomy slug covers a candidate type — block with a `review-records` taxonomy-proposal task and an `unblock-on-taxonomy` condition rather than inventing a slug.'
---

## When to use

Use this skill to widen the catalog's coverage with **archetypal complex
systems**, not case studies. Typical triggers:

- A `system-class` slug exists in `taxonomy/source/system-classes.yaml`
  but no `registry/systems/sys-*` entry covers it yet.
- An entry in `config/priority-systems.yaml` is unfulfilled and
  `plan-backlog` Tier 0.5 has scheduled this scout.
- A reviewer has identified a missing organizational level worth
  cataloging (e.g. between molecule and cell, "molecular machine"
  belongs in the catalog).

Do **not** use this skill to:

- Surface specific instances or case studies (e.g. "C. elegans", "the
  NYSE", "the Amazon rainforest"). These are *examples within* a
  type-level entry's `canonical_examples`, not separate registry
  entries. See AGENTS.md "What counts as a system worth cataloging".
- Search the primary literature for novel systems. Type-level
  archetypes are textbook material; the inclusion criterion expects the
  scout to recognize them by name, not discover them.
- Finalize system definitions or extract measurements. This skill only
  proposes.

## Preconditions

- The task manifest supplies `topic` (required) and `budget` (optional, default 3). Read the manifest's `notes` field for an explicit budget override (e.g. "Budget: 2 candidate systems").
- Taxonomy exports are current — if `taxonomy/exports/labels.json` is missing or stale, run `uv run coc export-taxonomy` first.

## Procedure

1. Read the current system roster: `registry/systems/*/system.yaml` (just the `name`, `slug`, `status`, and `taxonomy_refs` fields). Skip duplicates and `status: deprecated` entries that are already replaced.
2. Read the taxonomy exports at [labels.json](../../taxonomy/exports/labels.json) to know the available `system-domain` and `system-class` slugs.
3. Read [config/priority-systems.yaml](../../config/priority-systems.yaml) to see what's been hand-curated as priority and what's already fulfilled (per the `Priority seed: <slug>.` notes-prefix idempotency rule).
4. For each candidate type-level system:
   - Confirm it satisfies the inclusion criterion in AGENTS.md (type not instance; distinct organizational level; recognizable characteristic structure; ≥3 well-known examples — or genuinely singular and noted; admits at least one cross-applicable metric).
   - Draft a 1-paragraph description of its archetypal boundary and components.
   - Pick one `system-domain` and one or more `system-class` slugs. If no slug fits, emit a `review-records` taxonomy-proposal task and use `--unblock-on-taxonomy` on the scout (see "Block or fail when").
   - Note 3+ canonical examples that would populate `canonical_examples` in the eventual profile (e.g. for `metabolic-network`: *E. coli* core metabolism, human red blood cell metabolism, methanogen archaea metabolism).
   - Identify 2-5 candidate metrics that would characterize the type. For each, check whether the metric already exists in `registry/metrics/`. If not, name it in the scout report; **do not emit `define-metrics` tasks from this skill** — metric definition is a separate, more deliberate curation pass that requires literature grounding.
   - **Source citation is optional** for the scout's profile-system proposal. Type-level entries don't require sources for their bare existence (per AGENTS.md). Include `source_refs` only if the candidate's existence or definition is genuinely contested in the literature.
5. Emit one `profile-system` task per accepted candidate into `ops/tasks/inbox/` with the proposed slug in `notes`, the canonical examples summarized in `notes`, and `source_refs` empty (or only foundational refs if relevant).
6. Write the scout report with sections: **Accepted**, **Rejected**, **Taxonomy gaps**, **Sources consulted (optional)**.
7. Validate the new task files: `uv run coc validate ops/tasks/inbox/`.

## Output shape

- `ops/tasks/inbox/tsk-*.yaml` — each valid against [task.schema.json](../../schemas/task.schema.json), `state: inbox`.
- `ops/runs/.../scout-report.md` — markdown with sections: Accepted, Rejected, Taxonomy gaps, Sources consulted.

## Acceptance tests (canonical)

Copy these strings verbatim into the `acceptance_tests` field of any
`scout-systems` task manifest (e.g. from `plan-backlog`). Do not rephrase;
substitute only the bracketed `<domain>` token when a specific
`system-domain` slug is being targeted. If no domain is targeted, drop the
parenthetical.

```yaml
acceptance_tests:
  - At least one profile-system task manifest is written to ops/tasks/inbox/
    for a <domain>-domain candidate, each carrying >=1 source_ref and
    naming a candidate system-domain / system-class slug pair that resolves
    against taxonomy/source/.
  - A scout-report.md is written under
    ops/runs/YYYY/MM/DD/<run-id>/scout-report.md with sections Accepted,
    Rejected, Taxonomy gaps, and Sources consulted.
  - '`uv run coc validate ops/tasks/inbox/` exits 0 on the emitted manifests.'
```

Rationale: `stop_conditions` describes when the skill may halt; it is not
phrased as pass/fail assertions a reviewer can check on the artifacts. The
block above is the canonical assertion shape, grounded in the outputs the
skill actually writes.

## Block or fail when

- Candidate volume exceeds `budget` × 3 — the topic is too broad; block with a narrower-topic proposal.
- All candidates were rejected (no viable systems) — block with `state: blocked`, reason = no-candidates-found.
- Any candidate's sources are exclusively behind paywalls we can't archive — note in the scout report but do not block (sources can be stubbed at `source-status: pending-acquisition`).
- No taxonomy slug covers a candidate system. Emit a `review-records` task proposing the taxonomy addition, then block **with an auto-unblock condition** so the scout re-enters `ready/` automatically once the slug lands:
  ```bash
  uv run coc complete <self-task-id> --state blocked \
    --unblock-on-taxonomy system-class:<proposed-slug>
  ```
  The next `coc advance` sweep (preflight of every autonomous run) checks `taxonomy/source/*.yaml`; when the slug resolves, the scout is moved back to `ready/` with `lease.attempts` reset to 0. Use `--unblock-on-task <tsk-id>` instead when the dependency is another task's completion rather than a taxonomy edit.

  **Priority-seed re-try.** This same flow covers `plan-backlog` Tier-0.5 priority seeds: a seed whose `class_hint` doesn't yet resolve carries the same `--unblock-on-taxonomy` condition (wired by Tier 0.5 itself, or by this skill on the first block), so the scout returns to `ready/` automatically once the paired `review-records` task lands the slug. No manual re-seed or follow-up `scout-systems` manifest is needed. plan-backlog's Tier-0.5 idempotency check (the in-flight `Priority seed: <slug>.` notes marker) keeps the seed singular across the block→advance cycle, and the empirical end-to-end pass is documented in retros `01KPYJSF5HEGXN72YQ3ETXPHPC`, `01KPYQCDMFVEMPG525BB5QEBEF`, and `01KPZPA0G4KFZ3E4QT703CGE51`.

## References

- [taxonomy/source/system-domains.yaml](../../taxonomy/source/system-domains.yaml)
- [taxonomy/source/system-classes.yaml](../../taxonomy/source/system-classes.yaml)
- [taxonomy/source/metric-families.yaml](../../taxonomy/source/metric-families.yaml)
- [schemas/task.schema.json](../../schemas/task.schema.json)
