0a. Study specs/* with up to 250 parallel Sonnet subagents to understand the intended behavior.
0b. Study @IMPLEMENTATION_PLAN.md if present.
0c. Study the relevant implementation in src/app/* (Flask backend) and frontend/src/* (React Islands frontend) using up to 250 parallel Sonnet subagents.
0d. Review recent git commits and git notes to understand why changes were made. Use Opus subagents when architectural reasoning or debugging is required.

Your task is to perform a comprehensive implementation review. Do NOT implement new functionality unless fixing a trivial issue required to validate correctness.

Your primary output is a complete REVIEW.md document that replaces any previous version. REVIEW.md should always reflect the current state of the project.

The review must verify:

1. Every acceptance criterion in specs/* is satisfied.
2. The implementation matches @IMPLEMENTATION_PLAN.md.
3. No placeholders, TODOs, stubs, mock implementations, temporary workarounds, or dead code remain.
4. The implementation follows the project's architecture with a single source of truth and avoids duplicate logic.
5. The backend remains server-authoritative where required and does not expose restricted internal state.
6. Error handling, validation, edge cases, and failure paths are implemented correctly.
7. Tests adequately cover the implemented functionality.
8. Existing tests still pass without regressions.
9. Documentation accurately explains why the implementation exists, not merely what it does.
10. Performance, maintainability, readability, and consistency with surrounding code are acceptable.
11. Search for skipped/flaky tests, commented-out code, FIXME/TODO markers, unnecessary logging, debugging artifacts, or partially completed implementations.
12. Search for duplicated logic or inconsistencies that should instead share common utilities or abstractions.

Create REVIEW.md with the following sections:

# Overall Status

PASS / FAIL

# Executive Summary

A concise overview of the current health of the project.

# Specification Compliance

For each specification:
- PASS / PARTIAL / FAIL
- Evidence
- Missing functionality

# Critical Issues

Issues that would prevent release.

# Functional Bugs

Verified bugs with reproduction information when available.

# Test Coverage

- Tests executed
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
- Data exposure
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

If issues are discovered:

- Update IMPLEMENTATION_PLAN.md with actionable implementation work.
- REVIEW.md should contain findings only.
- IMPLEMENTATION_PLAN.md should contain tasks.

Run all appropriate tests before finalizing REVIEW.md.

If trivial issues preventing validation are encountered, you may fix them before continuing the review.

IMPORTANT:

- REVIEW.md must always be regenerated from scratch.
- Do not append to old reviews.
- Do not assume functionality is missing; verify through code search.
- Prefer evidence over assumptions.
- Use Opus subagents for complex reasoning.
- Ultrathink before reporting specification mismatches.
- Focus on correctness over style.
- Output <promise>DONE</promise> after REVIEW.md has been written successfully.