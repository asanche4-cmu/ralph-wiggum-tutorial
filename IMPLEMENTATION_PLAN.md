# Implementation Plan — Minesweeper Step 2 (Difficulty Presets + Leaderboard)

## Status (updated 2026-07-20 — Step 2 implemented end-to-end)

> **Step 1 (Base System): ✅ COMPLETE and validated.**
>
> **Step 2 (Extension): ✅ COMPLETE.** Difficulty presets + persistent
> leaderboard implemented across backend, frontend, migrations, and tests. All
> validation surfaces pass with zero errors:
> - `pytest tests/` — **49 passed** (13 new: `test_presets.py` + `test_leaderboard.py`)
> - `mypy src/` — clean (19 files)
> - `flake8 src/ tests/` — clean
> - frontend `tsc` — clean; `eslint src/` — clean
> - frontend `vitest` — **13 passed** (new `Leaderboard.test.tsx`, extended `Controls.test.tsx`)
> - `playwright` — **9 passed** (3 new difficulty-dimension tests + 1 leaderboard test)

Specs:
- `specs/minesweeper-game.md` — Step 1 base.
- `specs/minesweeper-step2-extension.md` — Step 2 (all 9 acceptance criteria met,
  see mapping below).

---

## What was built (ground truth)

Backend (`src/app/`):
- `controllers/minesweeper.py` — `DIFFICULTIES` map (single source of truth):
  `beginner (9,9,10)`, `intermediate (16,16,40)`, `expert (16,30,99)`.
  `DEFAULT_DIFFICULTY='beginner'`. `new_game(rows, cols, mine_count, difficulty)`
  keeps its positional dimension signature (engine unit tests depend on it) and
  now also stores a `difficulty` label. `new_game_for_difficulty(name)` looks up
  the preset and raises `UnknownDifficulty` (→ API 400) for bad names. Reveal /
  flood-fill / win logic **unchanged** — engine stays dimension-driven.
- `models/game.py` — added `difficulty: Mapped[str]` (`String(16)`, non-null,
  default `'beginner'`).
- `models/score.py` — **new** `Score` model: `id`, `game_id` (FK→games.id,
  **UNIQUE**), `name`, `difficulty`, `seconds`, `created_at`. Carries
  `# type: ignore[name-defined, misc]` like `Game`.
- `models/__init__.py` — exports `Score`.
- `schemas/game.py` — `GameStateView` gained `difficulty`; `serialize_game`
  populates it. Redaction path untouched (verified by existing security tests).
- `schemas/score.py` — **new**: `SubmitScoreRequest(gameId, name)` with a
  `field_validator` that trims + rejects empty/over-20-char names (→ 400);
  `LeaderboardEntry(name, seconds, createdAt)`, `LeaderboardView(difficulty,
  entries)`, `serialize_leaderboard`. camelCase literal fields (matches
  `game.py`'s no-alias convention). `MAX_NAME_LENGTH = 20`.
- `controllers/leaderboard.py` — **new**: `top_scores(difficulty, limit=10)`
  (ascending by seconds, then created_at; filtered by difficulty).
  `record_score(game_id, name)` → returns `(difficulty, top_scores)`; raises
  typed `ScoreError` subclasses carrying HTTP status: `GameNotFound(404)`,
  `GameNotWon(422)`, `DuplicateScore(409)`, `InvalidTiming(422)`. Time is
  `round(ended_at − first_move_at)`, floored at 0 — **authoritative, server-only**.
- `views/responses.py` — **new** shared `json_error(message, status)` with a
  correct status→label map (400/404/409/422). Both `api.py` and `leaderboard.py`
  use it — fixes the old catch-all "Bad Request" label.
- `views/api.py` — `create_game` reads optional `difficulty` (missing/empty →
  beginner default, preserving base no-body behaviour; unknown non-empty → 400).
  Uses shared `json_error`.
- `views/leaderboard.py` — **new** `leaderboard_bp`: `GET /api/leaderboard?difficulty=`
  and `POST /api/leaderboard`. Registered in `views/__init__.py` at `/api`.
- `migrations/versions/b2c3d4e5f6a7_add_difficulty_and_scores.py` — **new**, on
  head `a1b2c3d4e5f6`: adds `games.difficulty` (server_default `'beginner'` so
  existing rows backfill) + creates `scores` (unique `game_id`).

Frontend (`frontend/src/`):
- `minesweeper/types.ts` — `Difficulty`, `DIFFICULTIES` (value+label list),
  `difficulty` on `GameStateView`, `LeaderboardEntry`, `LeaderboardView`.
- `minesweeper/api.ts` — `request<T>` now generic. `createGame(difficulty)`,
  `getLeaderboard(difficulty)`, `submitScore(gameId, name)`; `AlreadyRecordedError`
  thrown on 409.
- `minesweeper/useGame.ts` — `newGame(difficulty)`; exposes current `difficulty`.
- `minesweeper/Controls.tsx` — difficulty `<select data-testid="difficulty">`;
  now uses the shared `GameStatus`/`Difficulty` types (inline union removed).
- `minesweeper/Leaderboard.tsx` — **new** best-times table; refetches on
  `difficulty`/`refreshKey` change; empty state.
- `minesweeper/WinDialog.tsx` — **new** name-entry form; reflects
  submitting/recorded/error states.
- `components/MinesweeperIsland.tsx` — mount default stays Beginner; win → prompt
  → `submitScore` → bump leaderboard refresh; 409 handled as "already recorded";
  mounts `Leaderboard`.

Tests:
- `tests/test_presets.py` — preset dims/mine counts (controller + API);
  unknown → 400; **no-body create still defaults to Beginner** (regression guard).
- `tests/test_leaderboard.py` — security-style: playing/lost → 422; double → 409;
  unknown game → 404; empty/over-long name → 400; name trimmed; **client-supplied
  duration ignored** (exact `seconds` from seeded timestamps); listing sorted
  ascending + partitioned by difficulty; persistence via `expire_all` + re-read.
- `frontend/tests/minesweeper/Leaderboard.test.tsx` + extended `Controls.test.tsx`.
- `e2e/minesweeper.spec.ts` — 81/256/480-cell difficulty tests + leaderboard
  visibility/filter follows selector.

---

## Acceptance-criteria mapping
1. Selector offers all three presets — ✅ `Controls.tsx` + `types.ts::DIFFICULTIES`.
2. Selecting starts correct-size server board — ✅ `useGame.newGame` → `createGame` →
   `new_game_for_difficulty`; E2E cell-count tests.
3. Base gameplay works at every difficulty — ✅ engine unchanged, dimension-driven.
4. Win → submit name, time recorded — ✅ `WinDialog` + `POST /api/leaderboard`.
5. Time computed authoritatively server-side — ✅ `record_score` from timestamps;
   no client duration field; proven by `test_client_supplied_duration_is_ignored`.
6. Score only for `won` game, only once — ✅ status check (422) + unique FK (409).
7. Leaderboard per difficulty, ascending, filtered — ✅ `top_scores` + partition test.
8. Persists across restarts — ✅ DB-backed; `TestPersistence` re-reads after expire.
9. All validation commands pass — ✅ (see Status).

---

## Remaining / optional (non-blocking)

- **Deterministic-win E2E** — NOT added, by design. Mines are placed randomly on
  first click and there is **no UI mine-injection path**, so a guaranteed win
  can't be driven through the browser without a test-only seed endpoint. That
  endpoint was deliberately not added to keep production paths clean. The full
  win → submit → leaderboard flow is covered by backend API tests
  (`test_leaderboard.py`) + frontend unit tests (`Leaderboard`, `Controls`).
  If a UI-level win assertion is later required, add a testing-config-gated seed
  endpoint (inject `mine_positions`) and assert the WinDialog → leaderboard path.
- **Datetime deprecation (Phase 0, hygiene)** — 4 `datetime.utcnow()` sites
  (`models/game.py`, `controllers/minesweeper.py` ×2, `models/score.py` default)
  still emit `DeprecationWarning`. Not a blocker (naive subtraction works; all
  sites are consistently naive). If cleaned up, migrate all sites in one pass to
  `datetime.now(timezone.utc)` to avoid mixing naive/aware.
- **Dead `getGame` export** (`api.ts`) — still exported, still unused. Wire into a
  resume flow or delete.

## Watch-outs for future work
- Beginner MUST remain the no-body `POST /api/games` default (base API test + E2E
  `'010'`/81-cells depend on it).
- New 409/422 come from `views/responses.py::json_error` — keep the label map current.
- `vite build` empties `src/app/static/` (removes `.gitkeep`); restore after a prod build.
- E2E on Windows: relative sqlite resolves to `src/instance/`; reuse a running
  Vite/Flask (`reuseExistingServer`); always `--reporter=list` (see `AGENTS.md`).
