---
retro_id: retro-01KQ3BSE00BN3Q0Q4GAYK26PAB
run_id: run-01KQ3BSE00YJGXVEZ5Z3WH7MRG
task_id: tsk-20260425-000013
skill: acquire-source
timestamp: 2026-04-25T22:57:30Z
agent: claude-code/run-01KQ3BSE00YJGXVEZ5Z3WH7MRG
actionable: true
confidence: high
what_worked:
  - "Dispatch raises UnsupportedRefError immediately on isbn: refs (no network round-trip), so the block decision was instantaneous and the lease window was minimally consumed."
  - "The skill's `unsupported-ref` block reason is precisely defined and applies cleanly — no judgment call needed."
blockers:
  - "Plan-backlog Tier 0.75 emits acquire-source tasks for isbn: refs that are guaranteed to block at lease time. Six isbn-prefixed acquire-source tasks have queued through this loop in two days (tsk-20260425-000013, 000014, 000021, 000022, 000023, plus tsk-20260425-000025 for a non-isbn DOI but in the same retro cohort). Each one consumes a Branch-A iteration slot purely to mark it blocked. That's a workflow leak — the iteration budget is meant to advance catalog state, not to repeatedly confirm the absence of an isbn resolver."
proposed_improvements:
  - target: skills/plan-backlog/SKILL.md
    change: >
      In Tier 0.75, skip emission for isbn: refs while no isbn-resolver is
      registered (introspect AUTO_PROMOTE_TYPES + acquire-source's resolver
      list, or just hard-code the skip on isbn: with a TODO until a book-
      metadata resolver lands). Either drop the ref silently with a one-line
      log entry in the plan-report's Skipped section, or emit a single
      `review-records` task (priority: low) hinting that a manual-acquisition
      pathway is needed for the cohort of unresolved isbn refs across all
      blocked tasks (one task batched, not one per ref). Today's behavior is
      one acquire-source per isbn ref → guaranteed lease-and-block per ref;
      the skill's per-pass cap of 3 means each pass burns up to 3 iteration
      slots on this no-op even when other Branch-A work is available.
    rationale: >
      Six confirmed iterations consumed by this loop in two days. The skill
      should pre-filter out refs whose resolver is missing rather than
      generating queue work that is provably blocked at the moment of
      emission. Closes the workflow leak without prejudging when/whether a
      book-metadata resolver lands.
    severity: moderate
  - target: src/coc/sources/dispatch.py
    change: >
      Add an isbn: resolver that fetches metadata-only via a free service
      (Google Books API, Open Library, or both with fallback). Mirror the
      DataCite-fallback pattern from the major proposal in
      retro-01KQ3BDZ6KK51AFW5MBE1H3H68: write metadata.json to raw/ from
      the API response, leave license: null, allow downstream
      extract-observations tasks to block on full-text only when needed.
      Both Google Books and Open Library publish ISBN-keyed JSON endpoints
      with no auth requirement.
    rationale: >
      Removes the structural reason for the workflow leak the moderate
      proposal above patches around. Six already-blocked isbn: refs in the
      queue today (Epstein & Pojman, Field & Burger, Griffiths quantum,
      Modern QC, Palsson, etc.) cover canonical references the catalog
      will repeatedly need for chemistry/physics/biology profiles.
      Metadata-only is sufficient for citation grounding; full-text is a
      separate concern.
    severity: major
---

## What happened

Leased `tsk-20260425-000013` (acquire-source, isbn:9780471893844 = Field
& Burger eds. 1985, *Oscillations and Traveling Waves in Chemical
Systems*, Wiley). `coc acquire` raised `UnsupportedRefError` immediately
because src/coc/sources/dispatch.py routes isbn: to a stub that throws.
Blocked the task as `unsupported-ref` per the skill — the textbook case
of the rule.

## Friction

The block itself is correct, but the upstream is the plan-backlog Tier
0.75 sweep emitting these tasks at all. The sweep scans `source_refs`
blindly without checking whether the ref's prefix has a registered
resolver. With six isbn-prefixed acquire-source tasks queued in two days
(this one, tsk-20260425-000014 / 000021 / 000022 / 000023, and the
follow-on cohort), each one consumes a full Branch-A iteration to mark it
blocked — pure overhead. Two proposals: the moderate one closes the leak
in plan-backlog by skipping isbn: emission; the major one closes it by
adding an isbn: resolver via Google Books / Open Library so the refs
actually resolve.

## Follow-up

Per the retrospective skill's contract for severity: major, emit a
follow-up review-records task to inbox/ describing the isbn-resolver
implementation. Done as `tsk-20260425-000028`.
