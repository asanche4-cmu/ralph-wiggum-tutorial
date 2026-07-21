# Implementation Plan — Minesweeper Step 2 (Difficulty Presets + Leaderboard)

## Status (updated 2026-07-20, re-verified against source — 4-agent parallel sweep)

> **Step 1 (Base System): ✅ COMPLETE and validated.** Server-authoritative
> single-difficulty (9×9, 10 mines) Minesweeper, end-to-end.
>
> **Step 2 (Extension): ⬜ NOT STARTED.** Re-confirmed 2026-07-20 by a fresh
> parallel sweep of the extension spec, backend (`src/app/**`), frontend
> (`frontend/src/**`), tests (`tests/**`, `frontend/tests/**`, `e2e/**`), and
> `migrations/**` — **zero** difficulty/preset/leaderboard/score implementation
> exists. Every hit for those words is a forward-looking comment/docstring
> (`controllers/minesweeper.py:26,83`, `models/game.py:16,41-42`,
> `Controls.tsx:6-7`, `script/db-seed:7`), spec text, or a review note
> (`REVIEW.md:14,65-79,187-206` — prior review recorded "0 of 9" ACs met).
> No `Score` model/controller/view/schema, no `DIFFICULTIES` map, no `difficulty`
> column or migration, no `getLeaderboard`/`submitScore` client fns, no
> `Leaderboard.tsx`/`WinDialog.tsx`. No TODO/FIXME/stub markers and no
> skipped/xfail/flaky tests exist in any source or test file.

Specs:
- `specs/minesweeper-game.md` — Step 1 base (the Step-2 spec header calls it
  `minesweeper-step1-base.md`; that filename does **not** exist on disk — same
  role, different name). All 10 base acceptance criteria met.
- `specs/minesweeper-step2-extension.md` — Step 2. **This plan targets it.**

Validation surfaces (must all pass with zero errors — see `AGENTS.md §26-37`):
- `script/setup` → apply migrations + deps (Alembic auto-applied).
- `script/test` → `pytest tests/ -v` + `cd frontend && npm test` (vitest run).
- `script/typecheck` → `mypy src/` + `cd frontend && npm run typecheck` (tsc).
- `script/lint` → `flake8 src/ tests/` + `cd frontend && npm run lint` (eslint).
- `script/test-e2e` → `npx playwright test`. **Scripts do NOT pass
  `--reporter=list`; you must add it manually** — the default html reporter
  blocks agents/CI (`AGENTS.md:31,59`). On Windows use the manual SQLite server
  workaround (`AGENTS.md:49-60`); the `webServer: script/server` auto-start
  fails under cmd.exe.

---

## Confirmed current state (ground truth for Step 2)

Backend (`src/app/`):
- `models/game.py` — `Game` (`__tablename__='games'`) has `id, rows, cols,
  mine_count`, JSON `mine_positions`(nullable)/`revealed`/`flags`, `status
  String(16)` default `'playing'`, and timing `started_at`(default
  `datetime.utcnow`, at `:55-57`)/`first_move_at`(`:58`, nullable)/`ended_at`
  (`:59`, nullable). All `DateTime` are **naive**. **No `difficulty` column.**
  Note the stale comment at `:41-42` ("difficulty presets need no schema change")
  — the spec overrides it (see decision #1). `class Game(db.Model)` already
  carries `# type: ignore[misc]` (`:34`) — copy this onto the new `Score` model.
- `controllers/minesweeper.py` — single board rule module. Constants `ROWS=9,
  COLS=9, MINE_COUNT=10` (**no `DIFFICULTIES` map**). `new_game(rows, cols,
  mine_count)` (`:66`) is dimension-parameterized but has **no `difficulty`
  arg**. Flood-fill is iterative (explicit stack, `:134-141`) — engine is fully
  dimension-driven, so all three sizes should work unchanged. `datetime.utcnow()`
  at `:99` (place_mines→first_move_at), `:128` (reveal loss→ended_at), `:177`
  (is_won→ended_at).
- `views/api.py` — `api_bp`, registered with `url_prefix='/api'` in
  `views/__init__.py:19`. Routes: `POST /games` (`create_game` reads **no body**,
  calls `new_game()` with no args → 201), `GET /games/<id>`, `POST
  /games/<id>/reveal`, `POST /games/<id>/flag`. Error via `_error(msg, status)`
  (`:37-40`) as direct JSON — labels 404 "Not Found", **everything else "Bad
  Request"** (so 409/422 would get a wrong label without a fix). **Only 200/201/
  400/404 exist; no 409/422.**
- `schemas/game.py` — `MoveRequest`, `CellView`, `GameStateView`. camelCase are
  **literal field names** (`gameId/mineCount/flagsUsed`), **no Pydantic aliases /
  no `ConfigDict`** in use today. `serialize_game`/`_cell_view` is the redaction
  choke point (mines only surfaced when `status=='lost'`). **No `difficulty`
  field; no score/leaderboard schema.** `__all__` = 4 names.
- `errors.py` — handlers for 400/404/500/Exception only. **The API bypasses this**
  (uses its own `_error`), so 409/422 must be produced in the API layer.
- `models/__init__.py` — `__all__ = ['db', 'Game']`.
- Migrations at **repo-root** `migrations/versions/`. Head = **`a1b2c3d4e5f6`**
  (chain: `e31396db40b1` → `f1a2b3c4d5e6` → `a1b2c3d4e5f6`).

Frontend (`frontend/src/`):
- `minesweeper/types.ts` — `CellState`, `GameStatus`, `CellView`, `GameStateView`
  (`gameId/rows/cols/mineCount/flagsUsed/status/board`). **No `Difficulty` or
  leaderboard types.**
- `minesweeper/api.ts` — `createGame()` (**no args**), `reveal`, `flag`, `getGame`
  (**exported, never imported — dead**). No `getLeaderboard`/`submitScore`.
- `minesweeper/useGame.ts` — `newGame()` (no args), `revealCell`, `flagCell`. No
  difficulty exposed.
- `minesweeper/Controls.tsx` — mine counter / face+new-game / display-only timer.
  `threeDigits()` zero-pads to 3 digits. **No difficulty selector.** `status`
  typed as an **inline literal union** (not the `GameStatus` type).
- `minesweeper/Board.tsx` — grid is `gridTemplateColumns: repeat(state.cols,…)`,
  fully data-driven; no hardcoded dims. Expert (30 cols) should render as-is.
- `components/MinesweeperIsland.tsx` — auto-creates a game on mount; client timer
  (starts once a cell is revealed, stops on end); win/loss banner. **No
  win-submission flow, no leaderboard mount.**
- `islands/minesweeper/index.tsx` mounts `<MinesweeperIsland/>` ignoring props;
  `main.ts` registers exactly one island (`minesweeper`).

Tests (all hardcode the 9×9/10 base — **Beginner MUST remain the default** or
these regress):
- `tests/conftest.py` — `app` fixture uses `create_app('testing')` with
  `db.create_all()`/`drop_all()` per test (in-memory SQLite). No time/RNG mocking
  — so leaderboard timing tests must **seed `first_move_at`/`ended_at` directly**
  on the `Game` row to assert exact `seconds` (mirror the existing loss-injection
  pattern).
- `tests/test_minesweeper_logic.py` — engine units incl. a deterministic **win**
  (all-safe-cells flood → `STATUS_WON` + `ended_at`), mines injected via
  `mine_positions`. **One RNG-dependent test** (`TestFirstRevealSafety`, 50 fresh
  games) is the *only* test relying on real randomness — everything else injects
  mines. This injection pattern is the template for a deterministic Step-2 win.
- `tests/test_api_game.py` — `_create` POSTs **no body**, expects 201 + `rows==9,
  cols==9, mineCount==10`. Redaction-security tests inject `mine_positions`
  **and set `first_move_at`** directly, then reveal a mine to force deterministic
  loss (the exact DB-injection recipe reusable for a deterministic win + score).
- `tests/test_game_view.py` — HTML shell + 404 handlers.
- `frontend/tests/minesweeper/{Cell,Controls}.test.tsx` — Controls asserts
  `'007'`/`'-02'`/`'042'` (the 3-digit counter contract). **The `'010'` / `'009'`
  mine-counter strings live in E2E, not vitest.**
- `e2e/minesweeper.spec.ts` — asserts **81 cells**, mine-counter **`'010'`**,
  flag→**`'009'`**, timer starts on reveal, and a **loss** end-of-game (clicks all
  81 cells in order). **No deterministic WIN, no difficulty/leaderboard coverage.**
- **No difficulty/leaderboard/score tests anywhere. No skipped/flaky tests.**

---

## Cross-cutting design decisions (resolve before coding)

1. **Add a `difficulty` column to `games`.** Spec requires it (§Step 2,
   `GameStateView` must surface it, leaderboard partitions by it). Overrides the
   stale `models/game.py:41` comment. → new migration.
2. **`DIFFICULTIES` map is the single source of truth** in `controllers/
   minesweeper.py`: `{'beginner': (9,9,10), 'intermediate': (16,16,40),
   'expert': (16,30,99)}`. `new_game(difficulty)` looks it up; do NOT special-case
   per difficulty in reveal/flood-fill/win (engine stays dimension-driven — spec
   §Notes explicitly forbids editing engine logic for presets).
3. **⚠️ DECISION — `difficulty` required vs optional on `POST /api/games`.** Spec
   API Contract says the body is "now `{difficulty}`" and unknown values → 400,
   but does NOT explicitly say a *missing* difficulty → 400. `test_api_game.py`
   `_create` POSTs **no body** and expects 9×9/10; the E2E auto-created game
   expects `'010'`/81 cells. **Recommendation: keep `difficulty` OPTIONAL,
   default `'beginner'`; reject only unknown non-empty strings with 400.** This is
   spec-compatible and non-regressing. If the grader treats a missing field as a
   400, instead update the base create tests + make the island send `'beginner'`
   explicitly on mount — flag this to the user before choosing.
4. **Authoritative timing.** `seconds = ended_at − first_move_at`, computed
   server-side in `record_score`; ignore any client-supplied duration. Store as
   `int` — **pick round vs truncate and assert the exact value in a test with
   seeded timestamps** (spec §Testing wants exact `seconds`).
5. **Timing already works today** — both `first_move_at` and `ended_at` are naive
   and set by the same code, so their subtraction is valid *now*. The
   `datetime.utcnow()` deprecation is **hygiene, not a blocker** (see Phase 0,
   deprioritized). If you do migrate to `datetime.now(timezone.utc)`, migrate all
   4 sites in one pass so stored values never mix naive/aware.
6. **New HTTP status codes.** Introduce 409 (duplicate) and 422 (game not `won`).
   Spec permits "400/422 if the game is not won" — **422 recommended**, but 400 is
   also spec-legal. Produce them via the API's own `_error` helper and **fix its
   label logic** (`views/api.py:39`) so 409→"Conflict"/422→"Unprocessable Entity"
   instead of the current catch-all "Bad Request". Also 404 (unknown game), 400
   (bad body/name/unknown difficulty).
7. **Duplicate prevention.** UNIQUE constraint on `scores.game_id` (FK→`games.id`)
   enforces one-score-per-game; `record_score` also checks status. (Spec says the
   FK "prevents duplicate submissions"; the unique constraint is the concrete
   mechanism.)
8. **Wire contract = camelCase.** New schemas need `gameId`, `createdAt` on the
   wire vs snake_case columns `game_id`, `created_at`. The existing `game.py`
   schema uses **literal camelCase field names, no aliases** — either keep that
   pattern (literal `gameId`/`createdAt` fields) OR introduce Pydantic
   `Field(alias=…)` + `model_config`. **Be consistent with `game.py`'s existing
   no-alias style** to avoid a mixed convention; decide once.
9. **Shared surface.** All new client types → `minesweeper/types.ts`; all fetch
   wrappers → `minesweeper/api.ts`; server schemas → `schemas/score.py` +
   additions to `schemas/game.py`. No ad-hoc duplicate type defs.
10. **Name validation.** Trim whitespace; reject empty; cap length (pick a bound,
    e.g. 20 chars) → 400. Decide and test the exact bound.
11. **Leaderboard `limit`.** Default top-N (pick, e.g. 10), ascending by
    `seconds`, filtered by difficulty.
12. **Blueprint registration.** If a separate `views/leaderboard.py` blueprint is
    used, register it where `api_bp` is registered (`views/__init__.py:19`) — spec
    §Relevant Files also mentions `src/app/__init__.py`; follow whichever the
    existing `register_blueprint` call site actually is (`views/__init__.py`).

---

## Remaining work — prioritized bullet list

### Phase A — Difficulty presets (backend) [START HERE]
- [ ] `controllers/minesweeper.py` — add `DIFFICULTIES` map (decision #2);
      refactor `new_game` to accept `difficulty: str` and look up dims; add a
      validation helper that signals unknown difficulty (API turns into 400).
      Keep numeric params or derive from the map. **Do not touch reveal/flood-fill/
      win.**
- [ ] `models/game.py` — add `difficulty: Mapped[str]` (`String(16)`, non-null,
      default `'beginner'`). Update the stale `:41` comment.
- [ ] `schemas/game.py` — accept optional `difficulty` (default `beginner`) on the
      create body; add `difficulty` to `GameStateView` + `serialize_game`.
      **Verify redaction is unaffected** (highest-risk area).
- [ ] `views/api.py` — `create_game` reads+validates `difficulty` (unknown → 400),
      passes to `new_game`; **preserve the no-body default (beginner)** so
      `test_api_game.py` and E2E `'010'`/81-cells still pass (decision #3).
- [ ] New Alembic migration on head `a1b2c3d4e5f6` — `add_column('games',
      difficulty)`. Can be combined with the `scores` migration or separate; keep
      the chain linear.

### Phase A' — Difficulty presets (frontend)
- [ ] `minesweeper/types.ts` — add `Difficulty = 'beginner'|'intermediate'|
      'expert'`; add `difficulty` to `GameStateView`.
- [ ] `minesweeper/api.ts` — `createGame(difficulty)`.
- [ ] `minesweeper/useGame.ts` — `newGame(difficulty)`; expose current difficulty.
- [ ] `minesweeper/Controls.tsx` — difficulty selector; selecting starts a new game
      at that difficulty. (Import `GameStatus` while here to fix the inline union.)
- [ ] `minesweeper/Board.tsx` — verify (no change expected) the 16×30 Expert board
      renders (already `repeat(cols,…)`).
- [ ] `MinesweeperIsland.tsx` — ensure the mount default stays Beginner so E2E base
      assertions hold.

### Phase B — Leaderboard backend
- [ ] `models/score.py` — `Score(id, game_id FK→games.id UNIQUE, name, difficulty,
      seconds, created_at)`; register in `models/__init__.py` `__all__`.
- [ ] Alembic migration — create `scores` table (unique on `game_id`).
- [ ] `schemas/score.py` — `SubmitScoreRequest(gameId, name)` with name
      trim/length validation; `LeaderboardEntry(name, seconds, createdAt)`. Match
      `game.py`'s camelCase convention (decision #8).
- [ ] `controllers/leaderboard.py`:
      - `top_scores(difficulty, limit)` → ascending by `seconds`, filtered by
        difficulty, capped at limit.
      - `record_score(game_id, name)` → 404 if no game; 422 (or 400) if
        `status != 'won'`; 409 if a `Score` already exists for that `game_id`;
        else compute authoritative `seconds = ended_at − first_move_at`, insert,
        return the updated leaderboard for that game's difficulty.
- [ ] `views/api.py` (or new `views/leaderboard.py` blueprint) — `GET
      /api/leaderboard?difficulty=`, `POST /api/leaderboard`. **Fix `_error` label
      logic to support 409/422** (decision #6); register the blueprint (decision
      #12).

### Phase C — Leaderboard frontend & win flow
- [ ] `minesweeper/types.ts` — `LeaderboardEntry` (name, seconds, createdAt).
- [ ] `minesweeper/api.ts` — `getLeaderboard(difficulty)`, `submitScore(gameId,
      name)`; handle 409 gracefully.
- [ ] `minesweeper/Leaderboard.tsx` — best-times table for selected difficulty;
      refresh after submission; filtered by difficulty.
- [ ] `minesweeper/WinDialog.tsx` (or inline) — name-entry prompt on win.
- [ ] `components/MinesweeperIsland.tsx` — on `status==='won'`, prompt for name →
      `submitScore` → refresh leaderboard; disable re-submit on 409. Mount
      `Leaderboard`. (Optional: wire the dead `getGame` export into a resume flow,
      or delete it.)

### Phase D — Tests & validation
- [ ] `tests/test_presets.py` — each preset yields correct dims/mine count;
      unknown difficulty → 400; no-body create still defaults to Beginner
      (regression guard for decision #3).
- [ ] `tests/test_leaderboard.py` (security-style) — cannot submit for
      playing/lost game (422/400); cannot double-submit (409); `seconds` derived
      from **seeded server timestamps** (assert exact value, prove client input is
      ignored); listing sorted ascending and partitioned by difficulty (an Expert
      time never appears under Beginner); unknown game → 404; empty/over-long name
      → 400/trim.
- [ ] `tests/test_leaderboard.py` (or a dedicated test) — **AC #8 persistence**:
      a recorded score is still returned by `top_scores` after a fresh session /
      re-query (proves DB-backed, not in-memory). *(New — the previous plan omitted
      this.)*
- [ ] Frontend unit tests — difficulty selector triggers `newGame(difficulty)`;
      `Leaderboard` renders entries; win flow calls `submitScore`. **Do not break
      the existing `'007'/'-02'/'042'` Controls contract.**
- [ ] `e2e/minesweeper.spec.ts` — selecting each difficulty renders the correct
      cell count (**81 / 256 / 480**); a deterministic win path prompts for a name
      and shows the time on the leaderboard; leaderboard filters by difficulty.
      **⚠️ Deterministic-win-in-E2E is hard**: the engine places mines randomly on
      first click, and the UI has no mine-injection path (API tests inject
      `mine_positions` directly at the DB). Decide a mechanism *before* writing this
      test — options: (a) a test-only seed/endpoint gated to the testing config,
      (b) a 1-mine-ish tiny scenario, or (c) drive the DB directly in the E2E
      harness. Flag the chosen approach; keep it out of production paths.
- [ ] Run all 4 validation scripts (+ `script/setup` for migrations); fix every
      failure. Confirm the base `'010'`/`'009'` E2E counters, 81-cell default, and
      `test_api_game.py` 9×9/10 still pass.

### Phase 0 — Datetime deprecation hygiene (OPTIONAL, deprioritized)
- [ ] *(Not a timing prerequisite — current naive subtraction already works.)*
      Optionally replace the 4 deprecated `datetime.utcnow()` sites
      (`models/game.py:56`, `controllers/minesweeper.py:99,128,177`) with
      `datetime.now(timezone.utc)`, in **one pass** to avoid naive/aware mixing,
      optionally with `DateTime(timezone=True)`. Confirm `pytest` stays green and
      DeprecationWarnings clear. Do only if pursuing cleanliness; it does not gate
      any acceptance criterion.

---

## Risks / watch-outs
- **Redaction leak** is the highest-risk area — all responses flow through
  `serialize_game`; adding `difficulty` must not alter hidden-cell redaction.
- **Default-difficulty regression** — Beginner must stay the no-body default or
  `test_api_game.py` (9×9/10) and E2E (`'010'`, `'009'`, 81 cells) break.
- **New status codes** (409/422) must come from the API's own `_error` path with a
  **fixed label** — the current helper labels all non-404 as "Bad Request".
- **camelCase convention drift** — match `schemas/game.py`'s existing no-alias,
  literal-field-name style (decision #8); don't half-introduce Pydantic aliases.
- **Deterministic E2E win** — no UI mine-injection exists; needs an explicit
  mechanism decision (Phase D).
- **Flood-fill stays iterative** (explicit stack) — already fine for 16×30 Expert.
- **`vite build` empties `src/app/static/`** (`vite.config.ts:36-38`,
  `emptyOutDir:true`) removing `.gitkeep` — restore after a local prod build.
- **Playwright** — always add `--reporter=list` (scripts don't); on Windows use
  the manual SQLite server per `AGENTS.md:49-60`.
- **mypy** — `class Game(db.Model)` needs `# type: ignore[misc]`; apply the same to
  the new `Score` model (`AGENTS.md`).

## Step-1 review carry-overs (fold into Step 2)
- [ ] Deprecated `datetime.utcnow()` → optional Phase 0 (no longer a blocker).
- [ ] Dead `getGame` export → wire into a resume flow or delete (Phase C).
- [ ] E2E has no deterministic **win** assertion → added by Phase D (with the
      mine-injection mechanism decision).
