# Overall Status

**PASS**

Every acceptance criterion in both specs is satisfied with positive, executed
evidence. All validation surfaces were run serially in this review and are
green (pytest 49, mypy clean, flake8 clean, vitest 13, tsc clean, eslint clean,
Playwright 9). The two behavioral gates required by the review prompt — the
server-authoritative redaction check (item 5) and first-click safety /
flood-fill (item 6) — were verified by execution, not by reading the source.

Two findings remain, both **Low** severity and non-blocking (a dead
`getGame` export and `datetime.utcnow()` deprecation warnings). Neither affects
correctness or any acceptance criterion.

# Executive Summary

The project is a server-authoritative Minesweeper (Step 1) extended with three
difficulty presets and a persistent leaderboard (Step 2). The architecture is
clean and matches `IMPLEMENTATION_PLAN.md` and both specs: the game engine in
`controllers/minesweeper.py` is fully dimension-driven and untouched by the
Step 2 additions; a single redacting serializer (`schemas/game.py`) is the only
path from `Game` to the wire; and the leaderboard trust boundary
(`controllers/leaderboard.py`) computes elapsed time solely from server-stored
timestamps with the submit schema deliberately carrying no duration field.

All tests pass and the security-critical properties hold under execution:
- A `playing` game's API response leaks **zero** mine/adjacency data for
  unrevealed cells (verified on an actual Intermediate response body).
- The first revealed cell (and its neighbors) is never a mine across 200 fresh
  games.
- Elapsed time cannot be forged from the client (a body carrying
  `seconds:1, duration:0` still records the seeded server time of 42s).

The health of the project is high. Recommended actions are cosmetic.

# Specification Compliance

## `specs/minesweeper-game.md` (Step 1 — Base System)

| AC | Verdict | Evidence |
|----|---------|----------|
| 1. `/` shows 9×9 board + counter/timer/new-game | **PASS** | E2E `renders a 9x9 board with controls` — 81 cells, mine-counter `010`, timer + new-game visible. |
| 2. Mines server-side, never in unrevealed responses | **PASS** | Behavioral probe: created an Intermediate game, revealed (8,8), server held 40 mine_positions; response board had 0 `mine` keys and 0 `adjacent` keys on the 226 unrevealed cells; raw JSON contained no `"mine"` substring. Also `test_playing_response_never_leaks_mines`. |
| 3. First revealed cell never a mine | **PASS** | Behavioral probe: 0 losses over 200 fresh Intermediate first-clicks. Unit `test_first_reveal_never_loses` (50 iterations) + `test_first_click_and_neighbors_are_safe`. |
| 4. Left-click reveals; zero cell flood-fills | **PASS** | `test_zero_cell_floods_contiguous_region` (24 cells revealed, mine excluded); `test_numbered_cell_does_not_flood`; E2E `revealing a cell starts the timer`. |
| 5. Right-click toggles flag + updates counter | **PASS** | E2E `right-click flags a cell and updates the counter` (counter `010`→`009`); `test_flag_toggles_and_updates_counter`. |
| 6. Revealing a mine → loss, shows all mines | **PASS** | `test_loss_exposes_full_mine_layout` (injected mines, all exposed on loss); E2E `revealing cells eventually ends the game`. |
| 7. All non-mine cells revealed → win | **PASS** | `test_revealing_all_safe_cells_wins`; `test_win_requires_all_safe_cells`. |
| 8. New-game button starts fresh board | **PASS** | `Controls` new-game wired to `newGame(difficulty)`; E2E board renders on load/selection. |
| 9. All Hello World code removed | **PASS** | Code search: no `hello` modules/imports remain in `src/`, `frontend/src/`, `tests/`, `e2e/`. |
| 10. All validation commands pass | **PASS** | See Test Coverage — all six surfaces green. |

## `specs/minesweeper-step2-extension.md` (Step 2 — Extension)

| AC | Verdict | Evidence |
|----|---------|----------|
| 1. Selector offers Beginner/Intermediate/Expert | **PASS** | `Controls.tsx` renders `DIFFICULTIES` (9×9/10, 16×16/40, 16×30/99); `types.ts::DIFFICULTIES`. |
| 2. Selecting a difficulty starts correct-size board | **PASS** | E2E `selecting {beginner,intermediate,expert} renders a {81,256,480}-cell board` — all pass; `test_create_with_difficulty` (parametrized dims). |
| 3. Base gameplay works at every difficulty | **PASS** | Engine is dimension-driven (unchanged); behavioral probe played an Intermediate board (reveal + flood-fill) successfully; E2E renders 480-cell Expert. |
| 4. On win, player submits name, time recorded | **PASS** | `test_records_authoritative_time` returns 201 with the entry; `WinDialog` + `MinesweeperIsland` submission flow; `submitScore` → `POST /api/leaderboard`. |
| 5. Time computed authoritatively server-side | **PASS** | `test_client_supplied_duration_is_ignored`: body `{seconds:1,duration:0}` still records seeded 42s. `record_score` derives `round(ended_at − first_move_at)`; `SubmitScoreRequest` has no duration field. |
| 6. Score only for `won` game, only once | **PASS** | `test_cannot_submit_for_playing_game`/`_lost_game` → 422; `test_cannot_double_submit` → 409 with exactly one row persisted; enforced by status check + `UNIQUE(scores.game_id)`. |
| 7. Leaderboard per difficulty, ascending, filtered | **PASS** | `test_sorted_ascending_and_filtered_by_difficulty` (beginner `[10,30]`, expert isolated); `top_scores` orders by `seconds, created_at`. |
| 8. Persists across restarts | **PASS** | DB-backed `scores` table (migration `b2c3d4e5f6a7`); `test_score_survives_reload` re-reads after `expire_all()`. |
| 9. All validation commands pass | **PASS** | See Test Coverage. |

# Critical Issues

None.

# Functional Bugs

None verified. All engine, API, redaction, and leaderboard behaviors matched
their specifications under execution.

# Test Coverage

## Tests executed (actual output summary)

| Command | Result |
|---------|--------|
| `pytest tests/` (`PYTHONPATH=src`) | **49 passed**, 81 warnings, 1.76s |
| `mypy src/` | **Success: no issues found in 19 source files** |
| `flake8 src/ tests/` | **clean** (exit 0) |
| `npm test` (vitest) | **13 passed** (Cell 5, Controls 5, Leaderboard 3) |
| `npm run typecheck` (tsc --noEmit) | **clean** (no output) |
| `npm run lint` (eslint) | **clean** (no output) |
| `npx playwright test --reporter=list` | **9 passed**, 6.9s |

E2E was run per the AGENTS.md Windows recipe: SQLite DB via `flask db upgrade`
(→ `src/instance/e2e_test.db`), Vite (:5173) and Flask (:5000) started manually,
Playwright reusing the running servers. All server/DB-touching commands were run
serially in a single context, never concurrently.

## Behavioral verification (beyond the suites)

- **Server-authority (item 5):** live Intermediate game, post-reveal response
  body inspected — 0 mine keys, 0 adjacent keys on 226 unrevealed cells, no
  `"mine"` in raw JSON, while the server row held 40 mines. PASS.
- **First-click safety (item 6):** 0 losses over 200 fresh first-clicks. PASS.

## Passing tests

All 49 backend + 13 frontend + 9 E2E tests pass.

## Failing tests

None.

## Coverage gaps

- **No UI-level win → submit → leaderboard E2E.** This is a deliberate,
  documented omission: mines are placed randomly on the first click and there
  is no UI mine-injection path, so a guaranteed win cannot be driven through the
  browser without a test-only seed endpoint (which was intentionally not added
  to keep production paths clean). The full win/submit/verify flow is covered by
  `test_leaderboard.py` (backend) and `Leaderboard`/`Controls` vitest. Acceptable.
- Frontend unit coverage for `WinDialog` and `useGame` is indirect (exercised via
  island composition rather than dedicated tests). Low impact; spec marks
  frontend unit tests optional.

## Missing regression tests

None material. The base-default regression guard
(`test_missing_body_defaults_to_beginner`) and the client-time-ignored guard are
both present.

# Architecture Review

- **Duplication:** None of concern. The status→label map was consolidated into
  `views/responses.py::json_error`, shared by both API blueprints, removing the
  base game's ad-hoc "Bad Request"-for-everything helper. `_coord_set`/`_as_set`
  appear in both `schemas/game.py` and `controllers/minesweeper.py`, but they
  serve different layers (serializer vs engine) and each is a 3-line helper —
  acceptable separation, not harmful duplication.
- **Separation of concerns:** Clean. Engine (rules) / schema (redaction) /
  controller (leaderboard trust) / views (HTTP↔controller) are well isolated.
  Views only translate HTTP and map `ScoreError.status` to codes.
- **Single source of truth:** `DIFFICULTIES` (backend) is the sole board-spec
  authority; `difficulty` is stored as its own column (not reverse-mapped from
  dimensions); the redacting serializer is the only `Game`→wire path.
- **API consistency:** Uniform camelCase (literal fields, no aliases) across
  `game.py` and `score.py`; all errors flow through one helper.
- **Technical debt:** Minimal — one dead export and deprecation warnings (below).

# Code Quality

- **Maintainability:** High. Modules are small, single-purpose, and documented
  with *why* rationale (the git note and module docstrings explain design
  decisions, e.g. why `new_game` kept its positional signature).
- **Readability:** High. Naming is consistent with surrounding code; the engine
  reads clearly (iterative flood-fill with an explicit stack, guard clauses).
- **Complexity:** Appropriate. Flood-fill is iterative (no recursion-overflow
  risk on Expert). No over-engineering.
- **Documentation:** Docstrings explain intent, not just mechanics (redaction
  guarantee, authoritative-timing rationale, first-click safety). `AGENTS.md`
  accurately captures the Windows E2E recipe, which reproduced cleanly.
- **Error handling:** Typed `ScoreError` subclasses carry their HTTP status;
  the view maps exceptions straight to responses. Bad JSON, wrong types, missing
  fields, and out-of-range coordinates are all handled (400).

# Security & Reliability

- **Validation:** Name trimmed + bounded (1–20 chars) in the request schema
  before the controller runs; unknown difficulty → 400; coordinates
  bounds-checked; malformed/non-JSON bodies → 400.
- **Error handling:** Distinct, correct codes — 404 (unknown game), 422
  (not won / missing timing), 409 (duplicate), 400 (bad input). Verified by
  tests.
- **State consistency:** `revealed` never contains a mine (guarded), so win
  detection is a safe count comparison; a won game always has both
  `first_move_at` and `ended_at`, and `InvalidTiming` guards the corrupt-row
  case with a clean 422 rather than a 500.
- **Data exposure (behavioral check):** CONFIRMED clean — a live `playing`
  Intermediate response exposed no mine positions or adjacency for any of its
  226 unrevealed cells while the server held all 40 mines. Mines are exposed
  only on loss, and only through the single serializer.
- **Concurrency issues:** None identified. Each request loads, mutates, and
  commits a single game row; duplicate submissions are additionally guarded by a
  DB-level unique constraint (defense in depth beyond the status check).
- **Performance concerns:** None. Leaderboard reads are single-table,
  `LIMIT 10`; board serialization is O(rows×cols).

# Recommended Actions

1. **Critical** — None.
2. **High** — None.
3. **Medium** — None.
4. **Low**
   - Remove the unused `getGame` export in `frontend/src/minesweeper/api.ts`
     (dead code — defined, never imported), or wire it into a reload/resume flow.
   - Migrate the four `datetime.utcnow()` call sites
     (`models/game.py`, `models/score.py`, `controllers/minesweeper.py` ×2) to
     `datetime.now(timezone.utc)` in one pass to silence the 81 deprecation
     warnings. Non-blocking (all sites are consistently naive, so subtraction is
     correct today).

# Overall Confidence

**High.** Every acceptance criterion is backed by an executed test or an
observed API response, including the two behavioral gates the review prompt
singles out. The only findings are cosmetic and already tracked.
