# Implementation Review — Server-Authoritative Minesweeper

_Reviewed: 2026-07-19 · Branch: `main` · HEAD: `1f5dcba`_

# Overall Status

**FAIL** — against the full specification set in `specs/`.

This verdict is scope-driven, not quality-driven. `specs/` contains **two** specs:

- `specs/minesweeper-game.md` (Step 1, Base System) — **fully implemented, all 10
  acceptance criteria met, all executable validation passes.** This is a clean PASS.
- `specs/minesweeper-step2-extension.md` (Step 2, Extension) — **not implemented at
  all** (no difficulty presets, no `Score` model, no leaderboard API/UI). 0 of 9
  acceptance criteria met.

Because Step 2's acceptance criteria are unmet, the aggregate status against everything
under `specs/` is FAIL. Note that `IMPLEMENTATION_PLAN.md` explicitly scopes Step 2 as
"NEXT WORK," so this is expected sequencing rather than a defect in delivered work. If the
review is scoped to "the currently delivered milestone (Step 1)," that milestone is a PASS.

# Executive Summary

The Step 1 base system is in excellent shape. It is a faithful, idiomatic implementation of
a server-authoritative Minesweeper: all secret state (mine positions, revealed/flag sets)
lives in the database, and every response is funneled through a single redacting serializer
(`serialize_game`) that provably prevents mine/adjacency leakage for unrevealed cells. The
engine is dimension-driven (not hard-coded to 9×9), flood-fill is iterative (no recursion
overflow risk), and first-click safety covers the clicked cell plus its 8 neighbors. Code is
well-documented with *why*-oriented comments, and the Hello World / Space Invaders scaffolds
are fully removed with no residual references.

All executable validation passes: **pytest 27/27, mypy clean (14 files), flake8 clean,
vitest 9/9, tsc clean, eslint clean.** The Playwright E2E suite was **not re-executed in this
review** (Windows manual-server workaround required — see Test Coverage); its source is
present and the plan claims 5/5.

Findings are limited to a few low-severity items: one unused exported frontend function
(`getGame`), a deprecated `datetime.utcnow()` usage that emits 68 warnings, and an E2E gap
(no deterministic win path is asserted). None block the Step 1 milestone.

# Specification Compliance

## `specs/minesweeper-game.md` — Step 1 (Base System): **PASS**

| # | Acceptance Criterion | Status | Evidence |
|---|----------------------|--------|----------|
| 1 | `/` shows a 9×9 board with mine counter, timer, new-game button | PASS | `templates/game.html` mounts `data-island="minesweeper"`; `MinesweeperIsland.tsx` renders `Controls` (counter/timer/new-game) + `Board`; E2E `renders a 9x9 board with controls` asserts 81 cells + counter `010`. |
| 2 | Mines stored server-side, never in responses for unrevealed cells | PASS | `models/game.py` holds `mine_positions`; `schemas/game.py::_cell_view` emits mine/adjacent only for revealed/lost; API uses `model_dump(exclude_none=True)`; `test_api_game.py::TestRedactionSecurity` asserts on the wire. |
| 3 | First revealed cell is never a mine | PASS | `controllers/minesweeper.py::place_mines` excludes safe cell + 8 neighbors; mines placed only on first reveal. `test_minesweeper_logic.py::test_first_reveal_never_loses` (50 iters), `test_first_click_and_neighbors_are_safe`. |
| 4 | Left-click reveals; zero cell flood-fills contiguous region | PASS | Iterative flood-fill in `reveal()`; `test_zero_cell_floods_contiguous_region`, `test_numbered_cell_does_not_flood`. |
| 5 | Right-click toggles flag and updates remaining-mine counter | PASS | `Cell.tsx` `onContextMenu` → `preventDefault` + `onFlag`; `Controls` shows `mineCount − flagsUsed`; `test_flag_toggles_and_updates_counter`, Cell/Controls unit tests, E2E flag test. |
| 6 | Revealing a mine → loss, shows all mines | PASS | `reveal()` sets `status=lost`; serializer exposes all mines when `lost`; `test_loss_exposes_full_mine_layout`. |
| 7 | Revealing all non-mine cells → win | PASS | `is_won()` count comparison; `test_revealing_all_safe_cells_wins`, `test_win_requires_all_safe_cells`. |
| 8 | New-game button starts a fresh board | PASS | `Controls` face button → `onNewGame` → `useGame.newGame()` → `POST /api/games`. |
| 9 | All Hello World code removed | PASS | No `hello`/`space invader` references remain in `src/`, `frontend/src/`, `tests/`, `e2e/` (grep clean); `db-seed` is a documented no-op; migration `f1a2b3c4d5e6` drops `hellos`. |
| 10 | All validation commands pass with zero errors | PASS (unit/type/lint) / UNVERIFIED (E2E) | pytest 27/27, mypy clean, flake8 clean, vitest 9/9, tsc clean, eslint clean. E2E not re-run this review. |

**Missing functionality:** none for Step 1.

## `specs/minesweeper-step2-extension.md` — Step 2 (Extension): **FAIL (not started)**

| # | Acceptance Criterion | Status |
|---|----------------------|--------|
| 1 | Difficulty selector (Beginner/Intermediate/Expert) | FAIL — not implemented |
| 2 | Selecting a difficulty starts a correctly-sized server board | FAIL |
| 3 | Base gameplay works at every difficulty | N/A — engine is dimension-ready but no preset path exists |
| 4 | On win, submit name; time recorded | FAIL |
| 5 | Server-authoritative completion time | FAIL |
| 6 | Score recorded only for `won` games, only once | FAIL |
| 7 | Leaderboard per difficulty, sorted ascending, filtered | FAIL |
| 8 | Leaderboard persists across restarts | FAIL |
| 9 | All validation commands pass | N/A |

**Missing functionality (complete):** `DIFFICULTIES` map + `new_game(difficulty)`;
`difficulty` column + migration; `Score` model + migration; `schemas/score.py`;
`controllers/leaderboard.py`; leaderboard API routes; frontend difficulty selector,
`Leaderboard.tsx`, win-submission flow, `getLeaderboard`/`submitScore`; `tests/test_presets.py`,
`tests/test_leaderboard.py`. The groundwork exists (per-game `rows/cols/mine_count`,
`first_move_at`/`ended_at` timestamps, dimension-driven engine and `Board`), so Step 2 is
additive as designed.

# Critical Issues

None for the delivered Step 1 milestone. The only release-blocking item relative to the full
`specs/` set is that Step 2 is entirely unimplemented (tracked in `IMPLEMENTATION_PLAN.md`).

# Functional Bugs

No verified functional bugs found in Step 1. Correctness spot-checks all held:

- Loss path returns before `is_won()`, so a mine in `revealed` never miscounts a win.
- A revealed mine can never appear while `status != lost` (revealing a mine sets `lost`), so
  the serializer's "expose mine only on loss" branch is consistent with the reveal logic.
- Flood-fill stack skips mines/flags/already-revealed, terminating correctly.
- Counter/`threeDigits` clamps to `[-99, 999]` for the over-flag display case.

# Test Coverage

**Executed this review:**
- `pytest tests/` → **27 passed** (logic, API redaction/security, view). ⚠️ 68
  `DeprecationWarning`s for `datetime.utcnow()`.
- `mypy src/` → **clean** (14 files).
- `flake8 src/ tests/` → **clean**.
- `frontend`: `vitest run` → **9 passed** (Cell 5, Controls 4); `tsc --noEmit` → **clean**;
  `eslint src/` → **clean**.

**Not executed:** Playwright E2E (`e2e/minesweeper.spec.ts`). On this Windows host the
`webServer: script/server` config fails under cmd.exe (documented in `AGENTS.md`), requiring a
manual SQLite server bring-up. Source is present (5 tests); the plan claims 5/5 previously.
This review does not independently confirm E2E green.

**Coverage gaps (low severity):**
- E2E asserts a game *ends* (loss via clicking every cell) but never asserts a **deterministic
  win path**, which the spec's Step 16 ("a seeded scenario reaches a win") calls for. The win
  banner is only exercised in unit-level `Controls` rendering.
- No frontend unit tests for `Board`, `useGame`, or `MinesweeperIsland` (the spec explicitly
  makes frontend unit tests optional and defers to E2E, so this is acceptable, not a defect).
- `getGame` (resume-after-reload) has backend coverage (`test_get_returns_current_state`) but
  the frontend never calls it, so the resume flow is untested end-to-end (spec permits "cleanly
  starts a new game" instead, which is what the island does).

**Missing regression tests:** none required for Step 1 beyond the win-path E2E gap above.

# Architecture Review

- **Single source of truth:** Strong. Board rules live only in
  `controllers/minesweeper.py`; the redaction guarantee lives only in
  `schemas/game.py::serialize_game`; the frontend wire contract lives only in
  `frontend/src/minesweeper/types.ts`. `count_adjacent` is defined once and reused by the
  serializer.
- **Duplication:** Minor and benign. `_as_set`/`_coord_set` (list-of-pairs → set-of-tuples)
  exists in both `controllers/minesweeper.py` and `schemas/game.py`. It's a 3-line helper
  duplicated across two layers that shouldn't depend on each other, so this is a defensible
  boundary rather than harmful duplication — noted for awareness.
- **Separation of concerns:** Clean. Model = state, controller = rules, schema = serialization/
  redaction, views = HTTP. Frontend mirrors this (api/types/hook/components/island).
- **API consistency:** Consistent — every state response goes through `_state_response` →
  `serialize_game`; errors return JSON directly (not `abort()`) so API clients get JSON
  regardless of `Accept`. Endpoints match the spec's API contract exactly.
- **Server authority:** Fully upheld. The client computes no outcomes; `useGame` short-circuits
  actions when not `playing` purely as a UX optimization, and the server independently rejects
  post-game moves.
- **Technical debt:** Low. The engine and `Board` are already dimension-driven for Step 2;
  timing columns are pre-wired. Pre-existing scaffold debt (`logging_config.py` branching on the
  never-set `app.config['ENV']`; stale `.github/skills/*` docs) is out of scope and noted in the
  plan.

# Code Quality

- **Maintainability / Readability:** High. Consistent naming, small focused functions, module
  docstrings that explain rationale.
- **Complexity:** Appropriate. Flood-fill is the only non-trivial algorithm and is clearly
  commented and iterative.
- **Documentation:** Strong and *why*-oriented (e.g., why mines are placed on first reveal, why
  JSON columns, why errors bypass `abort()`) — meets the "explains why, not what" bar.
- **Error handling:** `_parse_move` handles non-JSON bodies (`silent=True`), schema validation
  errors, and out-of-range coordinates, each → 400; unknown id → 404. No cell revealed/flagged
  guards are bypassable.
- **Dead code:** `getGame` in `frontend/src/minesweeper/api.ts` is exported but never imported
  anywhere (low severity).
- **Placeholders/TODOs/stubs:** None found (grep for TODO/FIXME/HACK/stub/placeholder/debugger
  clean). No stray `console.log`/`print`. `db-seed` is an intentional, documented no-op.

# Security & Reliability

- **Validation:** Request bodies validated via Pydantic; coordinates bounds-checked against the
  game's own dimensions before use.
- **Data exposure:** The core security property — mine/adjacency data never leaks for unrevealed
  cells during a `playing`/`won` game — is enforced in one place and directly tested
  (`TestRedactionSecurity`). Mines are exposed only when `status == lost`.
- **Error handling:** Failure paths (bad JSON, bad types, missing fields, out-of-range, unknown
  id) all return correct status codes with JSON bodies.
- **State consistency:** Loss/win finalization sets `status` + `ended_at` atomically within the
  reveal; `revealed` never contains a mine outside the loss cell.
- **Concurrency:** Each request loads → mutates → commits a single game row. No cross-request
  shared mutable state. Two concurrent reveals on the same game could interleave (last-writer-
  wins on the JSON columns), but this is a single-player game with no correctness guarantee
  required across simultaneous clients — acceptable for the spec.
- **Performance:** Serializer rebuilds the full board per response (O(rows×cols), with
  `count_adjacent` O(8) per revealed cell) — negligible for 9×9 and fine even for the future
  16×30 Expert board.

# Recommended Actions

1. **Critical** — Implement Step 2 (`specs/minesweeper-step2-extension.md`): difficulty presets,
   `Score` model + migration, leaderboard controller/API with server-authoritative timing and
   single-submission verification, and the leaderboard/win-submission frontend. Tasks are
   enumerated in `IMPLEMENTATION_PLAN.md`.
2. **High** — None.
3. **Medium** — Add a deterministic **win-path E2E** (seed/inject mine positions or reveal a
   known-safe sequence) to cover the win banner end-to-end, closing the spec Step 16 gap.
4. **Low** —
   - Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` in
     `controllers/minesweeper.py` and `models/game.py` to remove 68 deprecation warnings and
     store timezone-aware timestamps (relevant before Step 2's authoritative timing math).
   - Either wire `getGame` into a reload/resume flow in `useGame` or remove the unused export.
   - (Optional) Extract the shared `[row,col] → set[tuple]` helper if a common util layer is
     introduced in Step 2; not worth a dependency edge on its own today.

# Overall Confidence

**High** for the Step 1 assessment — verified through direct code reading and by executing the
full unit/type/lint suite (63 checks green). **Medium** on E2E specifically, which was not
re-executed in this environment. The Step 2 "not implemented" finding is certain (verified by
code search: no `Score` model, no leaderboard routes, no `DIFFICULTIES` map — only forward-
looking comments referencing them).
