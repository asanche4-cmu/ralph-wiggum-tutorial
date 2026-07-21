# Implementation Plan — Server-Authoritative Minesweeper

## Status

> **Step 1 (Base System): ✅ COMPLETE and fully validated (2026-07-19).**
> Space Invaders removed; server-authoritative single-difficulty (9×9, 10 mines)
> Minesweeper implemented end-to-end. All five validation surfaces pass:
> pytest 27/27, mypy `src/` clean, flake8 `src/ tests/` clean, tsc clean,
> eslint clean, vitest 9/9, Playwright E2E 5/5.

Specs:
- `specs/minesweeper-game.md` — Step 1, Base System. **All 10 acceptance criteria met.**
- `specs/minesweeper-step2-extension.md` — Step 2, difficulty presets + leaderboard (NEXT).

---

## Step 1 — what was built (for reference; do not redo)

Backend (`src/app/`):
- `models/game.py` — `Game` model: `rows/cols/mine_count`, JSON `mine_positions`
  (null until first reveal) / `revealed` / `flags`, `status`, `started_at`,
  `first_move_at`, `ended_at`. Registered in `models/__init__.py`.
- `controllers/minesweeper.py` — **single source of truth for board rules**:
  `ROWS/COLS/MINE_COUNT` constants, `new_game`, `place_mines` (first-click safety
  incl. 8 neighbors), `reveal` (iterative flood-fill, loss on mine), `toggle_flag`
  (over-flagging allowed), `is_won`. Dimension-driven so Step 2 presets need no rewrite.
- `schemas/game.py` — Pydantic v2 `MoveRequest`/`CellView`/`GameStateView` +
  `serialize_game` (**the redaction choke point**: hidden cells emit no
  `adjacent`/`mine`; mines exposed only when `status == 'lost'`; API uses
  `model_dump(exclude_none=True)`).
- `views/api.py` — `api_bp` (`/api`): `POST /games`, `POST /games/<id>/reveal`,
  `POST /games/<id>/flag`, `GET /games/<id>`. Errors returned as JSON directly
  (400 bad body / out-of-range, 404 unknown id) — not via `abort()`.
- `views/game.py` + `templates/game.html` — `<div data-island="minesweeper">`, title "Minesweeper".
- `migrations/versions/a1b2c3d4e5f6_create_games_table.py` — chained on `f1a2b3c4d5e6`.

Frontend (`frontend/src/`):
- `minesweeper/{types,api,useGame,Cell,Board,Controls}.tsx?` — types mirror server
  schema; `api.ts` typed fetch client; `Cell` (left-click reveal, right-click flag +
  `preventDefault`); `Board` dimension-driven grid; `Controls` (counter `mineCount−flagsUsed`,
  display-only timer, new-game); `useGame` holds `gameId`+state.
- `components/MinesweeperIsland.tsx` — composes Controls+Board, client timer (starts on
  first reveal, stops on end), win/loss banner. `islands/minesweeper/index.tsx` mounts it.
  Registered as `minesweeper` in `main.ts`.

Tests: `tests/test_minesweeper_logic.py`, `tests/test_api_game.py` (redaction/security),
`tests/test_game_view.py`, `frontend/tests/minesweeper/{Cell,Controls}.test.tsx`,
`e2e/minesweeper.spec.ts`.

Phase 0 cleanup done: SI engine/island/tests/e2e deleted; `script/db-seed` is now a
safe no-op; stale SI comments in `frontend/src/types/index.ts` refreshed.

---

## Reusable ground truth (still true, useful for Step 2)

- **DB targets:** dev/prod = PostgreSQL, tests = SQLite in-memory. Use `db.JSON` columns
  (portable across both). Migration head is now `a1b2c3d4e5f6`.
- **Schema lib = Pydantic 2.x.** Validate with `Model.model_validate(...)`, catch
  `ValidationError` → 400. Serialize with `model_dump(exclude_none=True)`.
- **No CSRF plumbing** (Flask-WTF not installed). JSON POSTs need no token.
- **`errors.py` content-negotiates** — API handlers return `jsonify(...), 4xx` explicitly.
- **mypy strict on `src/` only** (not `tests/`); flake8 covers `src/ tests/` (max-line 120).
  `class X(db.Model)` needs `# type: ignore[misc]` (flask-sqlalchemy 3.1.1 is typed but
  the base resolves through it as needs the ignore under `disallow_subclassing_any`).
- **E2E lives at repo root** (`e2e/`, `playwright.config.ts`). See AGENTS.md for the
  Windows/SQLite manual-server workaround (webServer `script/server` fails under cmd.exe).

---

## Step 2 (Extension) — NEXT WORK, prioritized

Base engine is dimension-driven; do NOT special-case per difficulty — thread dimensions through.

### Phase A — Difficulty presets
- [ ] `controllers/minesweeper.py` — add `DIFFICULTIES = {beginner:(9,9,10),
      intermediate:(16,16,40), expert:(16,30,99)}`; `new_game(difficulty)` looks up the preset.
      Reject unknown difficulty with 400 (validate in the API layer).
- [ ] `models/game.py` — add `difficulty` column (String). Migration to add it.
- [ ] `schemas/game.py` — `POST /api/games` body `{difficulty}`; add `difficulty` to `GameStateView`.
- [ ] `views/api.py` — read+validate `difficulty` on create.
- [ ] Frontend: `Difficulty` type, `createGame(difficulty)`, `newGame(difficulty)`, selector in
      `Controls.tsx`; confirm `Board` renders the wide 16×30 Expert board.
- [ ] `tests/test_presets.py` — assert dimensions + mine counts per preset; unknown → 400.

### Phase B — Leaderboard backend
- [ ] `models/score.py` — `Score(id, game_id FK→games, name, difficulty, seconds, created_at)`.
      Register in `models/__init__.py`. Migration for `scores` table.
- [ ] `schemas/score.py` — `SubmitScoreRequest(gameId, name)`, `LeaderboardEntry(name, seconds, createdAt)`;
      trim/limit name length.
- [ ] `controllers/leaderboard.py` — `top_scores(difficulty, limit)` (asc by seconds);
      `record_score(game_id, name)` verifies game exists + `status=='won'` + not already recorded;
      **authoritative `seconds = ended_at − first_move_at`** (ignore any client duration).
- [ ] `views/api.py` (or `views/leaderboard.py`) — `GET /api/leaderboard?difficulty=`,
      `POST /api/leaderboard` (409 duplicate, 400/422 non-won).
- [ ] `tests/test_leaderboard.py` — security tests: can't record non-won, can't double-submit,
      timing from server (seed timestamps to assert exact seconds), partitioned by difficulty.

### Phase C — Leaderboard frontend & polish
- [ ] `minesweeper/Leaderboard.tsx` + win-submission flow (name entry) in `MinesweeperIsland`;
      `getLeaderboard`/`submitScore` in `api.ts`; handle 409 gracefully.
- [ ] Extend `e2e/minesweeper.spec.ts`; verify Expert renders; run all 5 validation commands.

## Review findings (2026-07-19) — low-severity cleanup (see REVIEW.md)

These do not block Step 1 but should be addressed; the `datetime` item is worth
doing before Step 2's authoritative timing math.

- [ ] **Deprecated timestamps.** Replace `datetime.utcnow()` with
      `datetime.now(datetime.UTC)` in `controllers/minesweeper.py` (`place_mines`,
      `reveal` loss path, `is_won`) and `models/game.py` (`started_at` default).
      Removes 68 pytest `DeprecationWarning`s and makes stored timestamps
      timezone-aware — important because Step 2 computes `ended_at − first_move_at`.
- [ ] **Unused frontend export.** `getGame` in `frontend/src/minesweeper/api.ts` is
      exported but never called. Either wire it into a reload/resume flow in
      `useGame.ts` (spec allows resume via `GET /api/games/<id>`) or delete it.
- [ ] **Win-path E2E gap.** `e2e/minesweeper.spec.ts` asserts the game *ends* (loss)
      but never a deterministic **win**. Add a seeded/known-safe win path that
      asserts the win banner (spec Step 1, Step 16). Best folded into the Step 2
      E2E work that adds the win → name-submission flow.

## Risks / watch-outs
- **Redaction leak** is the highest-risk defect — all responses go through `serialize_game`; test directly.
- **Flood-fill stays iterative** (explicit stack) for the large Expert board.
- `vite build` empties `src/app/static/` (removes `.gitkeep`) — restore after a local prod build.
- Run Playwright with `--reporter=list` (html reporter blocks agents/CI).
- Pre-existing, NOT blockers: `logging_config.py` branches on `app.config['ENV']` (never set by
  modern Flask, so prod JSON logging never activates); stale docs in `.github/skills/*`
  (`test-in-browser`, `python-code-simiplifier`, `git-commit`) reference removed Hello/SI/`scripts/`.
