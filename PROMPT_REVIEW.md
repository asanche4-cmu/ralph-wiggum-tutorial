0a. Study `specs/*` with up to 250 parallel Sonnet subagents to understand the intended behavior.
0b. Study @IMPLEMENTATION_PLAN.md if present.
0c. Study the relevant implementation in `src/app/*` (Flask backend) and `frontend/src/*` (React Islands frontend) using up to 250 parallel Sonnet subagents.
0d. Review recent git commits and git notes to understand why changes were made (`git fetch origin refs/notes/commits:refs/notes/commits` then `git log --notes`). Use Opus subagents when architectural reasoning or debugging is required.

Your task is to perform a comprehensive implementation review. Do NOT implement new functionality unless fixing a trivial issue required to validate correctness (see the "trivial fixes" rule below).

Your primary output is a complete REVIEW.md document that replaces any previous version. REVIEW.md must always reflect the current state of the project and must be regenerated from scratch — never append to an old review.

## Evidence standard (read first)

You are reviewing code that may have been written by a peer agent. Do NOT grade leniently. Apply these rules:

- A criterion is PASS only with POSITIVE evidence: a test you executed and observed pass, or a concrete check you ran (e.g. an actual API response body). Reading the source and finding it "looks correct" is NOT sufficient for PASS.
- If you cannot verify a criterion by execution, mark it PARTIAL and say what evidence is missing. "Could not verify" is never PASS.
- Prefer evidence over assumptions. Do not assume functionality is missing; confirm with code search first. Equally, do not assume it works because the code is present.
- Ultrathink before reporting any specification mismatch.

## Test execution rules (IMPORTANT — avoid false failures)

Tests share resources: E2E starts a dev server on a fixed port and tests hit a shared database. Running them in parallel causes port/DB collisions and produces failures that are not real.

- Anything that builds, starts a server, or touches the database (`script/test`, `script/test-e2e`, `script/typecheck`, `script/lint`) MUST be run SERIALLY in a SINGLE subagent, one at a time. Never run two such commands concurrently.
- Only read-only searches and file reads may fan out across many subagents.
- Run all appropriate validation commands before finalizing REVIEW.md and record their actual output.

## The review must verify

1. Every acceptance criterion in `specs/*` is satisfied.
2. The implementation matches @IMPLEMENTATION_PLAN.md.
3. No placeholders, TODOs, stubs, mock implementations, temporary workarounds, or dead code remain.
4. The implementation follows the project's architecture with a single source of truth and avoids duplicate logic.
5. The backend remains server-authoritative where required and does not expose restricted internal state. VERIFY BEHAVIORALLY, not by reading the serializer: create an in-progress game via the API and inspect an actual response body, asserting that NO unrevealed-mine data (mine positions/adjacency for hidden cells) is present. A single leaking code path invalidates this even if the serializer looks clean.
6. First-click safety and flood-fill are correct. VERIFY with executed tests (seed/inject mine positions for determinism), not by static reading — these cannot be confirmed by inspection.
7. Error handling, validation, edge cases, and failure paths are implemented correctly.
8. Tests adequately cover the implemented functionality.
9. Existing tests still pass without regressions.
10. Documentation accurately explains WHY the implementation exists, not merely what it does.
11. Performance, maintainability, readability, and consistency with surrounding code are acceptable.
12. Search for skipped/flaky tests, commented-out code, FIXME/TODO markers, unnecessary logging, debugging artifacts, or partially completed implementations.
13. Search for duplicated logic or inconsistencies that should instead share common utilities or abstractions.

## Create REVIEW.md with the following sections

# Overall Status

PASS / FAIL. (PASS requires positive, executed evidence for every acceptance criterion — including the behavioral checks in items 5 and 6 above.)

# Executive Summary

A concise overview of the current health of the project.

# Specification Compliance

For each specification:
- PASS / PARTIAL / FAIL
- Evidence (the executed test or observed output supporting the verdict)
- Missing functionality

# Critical Issues

Issues that would prevent release.

# Functional Bugs

Verified bugs with reproduction information when available.

# Test Coverage

- Tests executed (with the actual command output summary)
- Passing tests
- Failing tests
- Coverage gaps
- Missing regression tests

# Architecture Review

- Duplication
- Separation of concerns
- Single source of truth
- API consistency
- Technical debt

# Code Quality

- Maintainability
- Readability
- Complexity
- Documentation
- Error handling

# Security & Reliability

- Validation
- Error handling
- State consistency
- Data exposure (include the behavioral server-authoritative check from item 5)
- Concurrency issues
- Performance concerns

# Recommended Actions

Prioritized list:

1. Critical
2. High
3. Medium
4. Low

# Overall Confidence

High / Medium / Low

## Findings vs. tasks

If issues are discovered:
- Update @IMPLEMENTATION_PLAN.md with actionable implementation work, using a subagent.
- REVIEW.md contains findings only.
- @IMPLEMENTATION_PLAN.md contains tasks only.

## Trivial fixes

If a trivial issue is blocking validation (e.g. a broken import, a missing test fixture, a typo'd command), you MAY fix it so the review can proceed. Anything non-trivial is a finding, not a fix — record it and move on. Do not implement new functionality.

## Commit (REQUIRED — do not skip)

The loop only pushes; it does not stage or commit for you. After REVIEW.md and @IMPLEMENTATION_PLAN.md are written:
1. `git add -A`
2. `git commit` with a message describing the review, e.g. `review: <PASS|FAIL> — <N> findings`
3. Log the review outcome to git notes for future reference.
The loop will push after you return.

## Final rules

- REVIEW.md must always be regenerated from scratch. Do not append to old reviews.
- Do not assume functionality is missing; verify through code search.
- Prefer evidence over assumptions. Focus on correctness over style.
- Use Opus subagents for complex reasoning.
- This is a SINGLE-PASS review — run it with `-n 1`. It reports the current state once; it does not iterate to green. (The DONE promise below fires whether the verdict is PASS or FAIL.)
- Output `<promise>DONE</promise>` only after REVIEW.md has been written AND the commit above has succeeded.