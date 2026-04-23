# Branch protection

The `master` branch is protected. Apply the rules below once after pushing
the repo; they are not applied automatically by anything in this directory.

## Required checks

- `validate / validate`
- `ci / lint`
- `ci / test (3.11)`
- `ci / test (3.12)`

## Required review

- At least one approving review from a CODEOWNER.
- Stale approvals dismissed on new commits.

## Merge rules

- Require branches to be up to date before merging.
- Require linear history.
- Disallow force pushes and deletions on `master`.

## Apply via `gh`

Run from a local clone once the repo exists on GitHub. Replace
`OWNER/REPO` as needed. The `required_status_checks.contexts` list must
match the job names produced by `.github/workflows/`.

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/OWNER/REPO/branches/master/protection \
  -F required_status_checks.strict=true \
  -F 'required_status_checks.contexts[]=validate / validate' \
  -F 'required_status_checks.contexts[]=ci / lint' \
  -F 'required_status_checks.contexts[]=ci / test (3.11)' \
  -F 'required_status_checks.contexts[]=ci / test (3.12)' \
  -F enforce_admins=true \
  -F required_pull_request_reviews.required_approving_review_count=1 \
  -F required_pull_request_reviews.dismiss_stale_reviews=true \
  -F required_pull_request_reviews.require_code_owner_reviews=true \
  -F required_linear_history=true \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F restrictions=
```
