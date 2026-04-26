---
name: acquire-source
description: Fetch one prefixed source reference (`doi:`, `arxiv:`, `url:`) and register it under `registry/sources/src-NNNNNN--<slug>/` with immutable raw artifacts and a validated source.yaml. The last step in the chain that turns an unresolved bibliographic reference into canonical catalog state.
status: active
inputs:
  - 'source_refs — exactly one entry. Accepted prefixes: `doi:<doi>`, `arxiv:<id>`, `url:<absolute-url>`. `isbn:` is reserved but not yet resolvable; block the task if one is passed.'
outputs:
  - '`registry/sources/src-NNNNNN--<slug>/source.yaml` — validated against schemas/source.schema.json.'
  - '`registry/sources/src-NNNNNN--<slug>/raw/` — one or more immutable artifact files (metadata + any OA full-text).'
  - '`registry/sources/src-NNNNNN--<slug>/parsed/` and `evidence.jsonl` — created empty; populated by downstream extract-observations tasks.'
stop_conditions:
  - 'source.yaml exists, validates, and its `hash` field matches the raw/ artifact bytes.'
  - 'An existing registered source already covers this reference (idempotent match on doi/arxiv/url) — skip write and report the existing src-id.'
  - 'The upstream returned 404 or equivalent — block with a `not-found` reason; do not create a stub.'
  - 'The upstream is reachable but no accessible full-text exists — metadata-only source.yaml is acceptable; record `license` = null and leave raw/ containing metadata artifacts only.'
---

## When to use

This is the *only* skill that writes to `registry/sources/<src>/raw/`. Use it
when any upstream task references an unregistered source with a prefixed
form (`doi:`, `arxiv:`, `url:`). Once the source is registered, downstream
tasks cite it by its `src-NNNNNN--<slug>` id instead.

`plan-backlog` Tier 0.75 (Source debt) scans in-flight and queued tasks for
unregistered prefixed refs and emits one `acquire-source` task per unique ref.

Do **not** use this skill to:

- Edit an existing source under `registry/sources/` — raw/ is immutable; a
  re-fetch produces a new `src-NNNNNN--<slug>` entry.
- Resolve `isbn:` refs — not yet supported; block.
- Run a literature search — that's `scout-systems` (and, later,
  `deep-search-systems`).

## Preconditions

- The task manifest has exactly one entry in `source_refs` with a supported
  prefix (`doi:`, `arxiv:`, `url:`).
- Environment variable `COC_CONTACT_EMAIL` is set (used in User-Agent and in
  the Unpaywall query parameter). Unset falls back to the default contact
  email; runs should override it for courtesy to the upstream APIs.
- Network access is enabled for the autonomous-run environment (see
  references below — Claude Code needs `WebFetch`, Codex needs a network
  allowlist covering `api.crossref.org`, `api.openalex.org`,
  `api.unpaywall.org`, `arxiv.org`, and publisher OA domains).

## Procedure

1. Read the task manifest's `source_refs` — exactly one entry expected.
2. Call `uv run coc acquire <ref>`. Under the hood:
   - `doi:` → Crossref metadata + Unpaywall OA lookup; fetches the OA PDF
     if one exists. If Crossref returns 404 (the DOI is not minted there
     — common for dataset / standards DOIs in the NIST `10.18434/*`,
     Zenodo `10.5281/*`, and figshare `10.6084/*` namespaces),
     dispatch falls back to DataCite's JSON:API for metadata-only
     resolution.
   - `arxiv:` → arXiv query API + PDF.
   - `url:` → generic GET; content-type determines `kind`.
3. The CLI writes `registry/sources/src-NNNNNN--<slug>/` atomically (stages
   under `.tmp-<src>/` and renames on success). On idempotency match, no
   new directory is created; the existing path is printed.
4. Run `uv run coc validate` on the new source.
5. Complete the task with `outputs` naming the registered src-id, e.g.
   `{"source_id": "src-000042--nrmicro3109"}`.

## Output shape

- `source.yaml` — every field per [schemas/source.schema.json](../../schemas/source.schema.json);
  `hash` is a SHA-256 over the ordered `raw/` artifact bytes.
- `raw/` — for DOI: `metadata.json`, `unpaywall.json`, optionally
  `paper.<ext>`. For arxiv: `metadata.xml`, optionally `paper.pdf`. For
  url: one `landing.<ext>`.
- `parsed/` — empty directory (populated by a future `parse-source` skill).
- `evidence.jsonl` — empty file (populated by `extract-observations`).

## Acceptance tests (canonical)

Copy verbatim into the `acceptance_tests` field of any `acquire-source` task
manifest. Substitute the bracketed `<ref>` token with the actual ref.

```yaml
acceptance_tests:
  - A directory registry/sources/src-*--<slug>/ exists for the ref <ref>,
    either newly written or an idempotent match reported by `coc acquire`.
  - That directory contains source.yaml (validating against
    schemas/source.schema.json) and a non-empty raw/ subdirectory.
  - source.yaml has non-null retrieved_at and hash (SHA-256 over raw/
    artifact bytes), and its kind is consistent with the resolver output.
  - '`uv run coc validate` exits 0.'
```

## Block or fail when

- The ref uses an unsupported prefix (`isbn:` today, or an unknown prefix)
  → block with reason `unsupported-ref`.
- The upstream returned 404 / the DOI is not minted at any of the queried
  registrars (Crossref *and* DataCite for `doi:`) / the arxiv id has no
  entry → block with reason `not-found`.
- Network failure (DNS, timeout, 5xx) persisting across retries → fail with
  reason `fetch-error`. The watchdog will retry up to `max_attempts`.
- The resolver produced a source record that fails schema validation →
  fail with reason `resolver-bug` and leave the task for review; this is a
  library bug, not an upstream problem.
- A paywalled source with no OA full-text is **not** a block: the skill
  writes a metadata-only source.yaml. Downstream `extract-observations`
  tasks that depend on full-text should block separately.

## References

- [schemas/source.schema.json](../../schemas/source.schema.json) — output
  contract for source.yaml.
- [schemas/task.schema.json](../../schemas/task.schema.json) — the
  `source_refs` prefix scheme (`doi:`, `arxiv:`, `url:`, `isbn:`).
- [src/coc/sources/](../../src/coc/sources/) — resolver implementations;
  extend by adding a new module + dispatch entry.
- [AGENTS.md](../../AGENTS.md) — the "never edit raw/" non-negotiable.
