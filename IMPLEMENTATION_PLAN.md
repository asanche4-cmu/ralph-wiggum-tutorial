# Implementation Plan — Server-Authoritative Minesweeper

## Status

> **Base System (Step 1): 0% implemented.** The current codebase is a fully
> working **client-side Space Invaders** game (commit `2310b40`). None of the
> Minesweeper backend, API, or frontend exists yet. The Space Invaders feature
> must be removed and replaced.

Specs:
- `specs/minesweeper-game.md` — Step 1, Base System (the ULTIMATE GOAL below).
- `specs/minesweeper-step2-extension.md` — Step 2, difficulty presets + leaderboard.

**ULTIMATE GOAL:** every acceptance criterion and validation command in
`specs/minesweeper-game.md` passes with zero errors — a complete,
server-authoritative, single-difficulty (9×9, 10 mines) Minesweeper.

---

## Ground truth (re-verified by parallel multi-agent code sweep, 2026-07-19)

> Re-confirmed this date via a **third** independent four-agent sweep
> (specs / backend / frontend / tests+scripts+config) of `specs/*`,
> `src/app/*`, `frontend/src/*`, `script/*`, plus a placeholder/stale-ref hunt.
> Every claim below still holds verbatim: Step 1 is **0% built**, the live
> codebase is a complete, working Space Invaders game, there are **no**
> Minesweeper source files (`controllers/minesweeper.py`, `models/game.py`,
> `schemas/game.py`, `views/api.py`, `frontend/src/minesweeper/`,
> `frontend/src/components/`, `frontend/src/islands/minesweeper/` all absent),
> **no** TODO/FIXME comments in `src/app` or `frontend/src`, and **no**
> skipped/xfail/flaky tests. `controllers/__init__.py` and `schemas/__init__.py`
> are docstring-only stubs (`__all__ = []`); `models/__init__.py` exports only `db`.


What the specs assume vs. what actually exists:

- **Hello World is already gone.** Migration `f1a2b3c4d5e6_drop_hello_table.py`
  already drops the `hello` table; `views/hello.py`, `models/hello.py`, `schemas/hello.py`,
  `controllers/hello.py`, and the Hello frontend no longer exist. **The spec's
  "remove Hello World" steps do not apply** — the equivalent work is **removing
  Space Invaders** (see Phase 0). After current migrations the DB has **no tables**.
- **No backend game logic exists:** `controllers/__init__.py` and
  `schemas/__init__.py` are empty stubs (`__all__ = []`). No `Game`/`Score` model,
  no `views/api.py`, no serializers.
- **No Minesweeper frontend exists:** `frontend/src/minesweeper/` and
  `frontend/src/components/` do not exist. `main.ts` registers only `game`
  (Space Invaders); `frontend/src/game/` and `frontend/src/islands/game/` are the
  Space Invaders engine + island.
- **Tests are Space Invaders:** `tests/test_game_view.py`, `frontend/tests/game/*`,
  `e2e/game.spec.ts`. `tests/conftest.py` exists (Flask app/client fixtures — reusable).
- **Infra is ready and reusable:** app factory (`src/app/__init__.py`) with
  Flask-Migrate wired; `db = SQLAlchemy(model_class=Base)` in `models/base.py`;
  blueprint registration in `views/__init__.py`; `base.html` island loader;
  `main.ts` island registry; `script/{setup,test,typecheck,lint,test-e2e}` all present.
- **DB targets:** dev/prod = PostgreSQL, tests = SQLite in-memory (`config.py`).
  Use `db.JSON` columns for `mine_positions`/`revealed`/`flags` — portable across both.
- **Schema library = Pydantic 2.x** (`requirements.txt`; `schemas/__init__.py` docstring
  says "Pydantic"). Build `MoveRequest`/`CellView`/`GameStateView` as `BaseModel`s;
  validate request bodies with `Model.model_validate(...)` and catch `ValidationError`→400.
- **No CSRF plumbing needed.** Flask-WTF is not installed; `WTF_CSRF_ENABLED = False` in
  `TestingConfig` is inert. JSON API POSTs require no CSRF token — don't add token machinery.
- **Migration head is `f1a2b3c4d5e6`** (verified: `down_revision = 'e31396db40b1'`, drops
  the `hello` table). The new `games` migration chains `down_revision = 'f1a2b3c4d5e6'`.
- **`views/__init__.py` registers only `game_bp`.** Add `api_bp` (url_prefix `/api`) there.
- **`frontend/src/types/index.ts` already exposes a generic `IslandProps<T>`** — keep it as-is
  (no Space Invaders types live there); only the `main.ts` registry entry `game` needs removal.
- **`errors.py` already returns JSON for 400/404/500** — but only via **content negotiation**
  (`Accept: application/json`). `flask.abort(404)`/`abort(400)` therefore render **HTML** unless the
  client sends that header. So the API client (`api.ts`) must send `Accept: application/json` **and/or**
  the API endpoints should `return jsonify(...), 4xx` explicitly rather than relying on `abort()`.
  Reuse this infra; don't add a second error layer.
- **`script/db-seed` is stale/broken** — it still does `from app.models import db, Hello` and seeds a
  `Hello` model that no longer exists. It is **not** in the validation-command set (`script/setup` does
  **not** call it; `script/test` doesn't import it), so it's a non-blocking cleanup, but leave it working:
  point it at `Game` or make it a no-op (base games are ephemeral, so a no-op is fine).
- **`.github/skills/test-in-browser/SKILL.md` is stale** — describes a Hello island and `/api/hello`
  routes that don't exist. Docs-only, non-blocking; refresh or delete when convenient.
- **Two more stale docs (newly found, docs-only, non-blocking):**
  `.github/skills/python-code-simiplifier/SKILL.md` references `scripts/lint`, `scripts/mypy`,
  `scripts/test` — but the dir is `script/` (singular) and there is no `mypy` script (type-checking is
  `script/typecheck`); `.github/skills/git-commit/SKILL.md` assumes a SQL `todos` table that doesn't
  exist here. Not in any validation command; refresh/ignore when convenient.
- **`base.html` and `tests/conftest.py` are generic and reusable as-is** — only `game.html` changes
  (title "Minesweeper", `data-island="minesweeper"`; currently title "Space Invaders",
  `data-island="game"`). `conftest.py` creates the schema via `db.create_all()`, so new-model tests
  work once `Game` is registered in `models/__init__.py`.
- **`src/app/static/` holds only `.gitkeep`** — no built assets. Prod (`VITE_DEV_MODE=False`) expects
  a Vite manifest under `static/`, so E2E/prod flows depend on a `vite build`; dev mode loads from the
  Vite dev server. Confirms the "vite build empties static/" watch-out below.
- **`logging_config.py` branches on `app.config['ENV']`**, which modern Flask no longer populates, so
  the production JSON-logging branch never activates. Pre-existing, unrelated to Minesweeper, and **not**
  a blocker — noted only so it isn't mistaken for new breakage. Leave as-is unless separately requested.
- **E2E lives at the repo root, not under `frontend/`.** `playwright.config.ts` and `e2e/game.spec.ts`
  are at the project root (there is **no** `frontend/e2e/` directory). `script/test-e2e` runs
  `npx playwright test "$@"`; the Playwright config auto-starts Flask (:5000) + Vite (:5173). So the new
  spec goes at root `e2e/minesweeper.spec.ts` and the SI `e2e/game.spec.ts` is deleted from the root.
- **Exact validation-command tool scopes** (so new code lands where the linters/type-checkers look):
  `script/typecheck` = `mypy src/` **then** `npm run typecheck` (tsc) — mypy covers **`src/` only**, so all
  new backend modules must be fully type-annotated; it does **not** type-check `tests/`. `script/lint` =
  `flake8 src/ tests/` **then** ESLint — flake8 **does** cover `tests/`, so new test files must pass flake8.
  `script/test` = `pytest tests/ -v` then vitest. All three use `set -e` (first failure aborts).

## Shared surface (consolidate here; avoid ad-hoc copies)

- **`src/app/schemas/`** — request/response schemas + the **redacting serializer**.
  This is the single choke point that must guarantee unrevealed mine data never
  leaks. Every API state response goes through it.
- **`frontend/src/minesweeper/types.ts` + `api.ts`** — the one place the TS types
  mirror the server schemas and the one typed fetch client. Board/Cell/Controls/
  hook all import from here.

## Spec-consistency notes (not blockers)

- The extension references `minesweeper-step1-base.md`; the actual base spec is
  `specs/minesweeper-game.md`. Documentation-only mismatch — no new spec needed.
- The base spec's "Relevant Files (remove)" list is stale (targets Hello, not
  Space Invaders). Follow Phase 0 below instead.

---

## Acceptance criteria → phase traceability (Step 1, all currently ✗)

The 10 base criteria (verbatim from `specs/minesweeper-game.md`) map to phases below:

1. `/` shows 9×9 board + mine counter + timer + new-game button → Phase 3 (`GET /`) + Phase 4.
2. Mine positions server-side, never in responses for unrevealed cells → Phase 1 (model) + redacting serializer + Phase 3; **security test in Phase 5**.
3. First revealed cell is never a mine (incl. 8 neighbors) → Phase 2 `place_mines`.
4. Left-click reveals; empty (zero) cell flood-fills contiguous region → Phase 2 `reveal` (iterative).
5. Right-click toggles flag + updates remaining-mine counter → Phase 2 `toggle_flag`, Phase 3 `flag`, Phase 4 `Controls`.
6. Revealing a mine → loss + shows all mines → Phase 2 loss path + Phase 3 (reveal returns full layout on loss).
7. Revealing all non-mine cells → win → Phase 2 `is_won`.
8. New-game button starts a fresh board → Phase 3 (`POST /api/games`) + Phase 4 `useGame`/`Controls`.
9. All Hello World code removed → **already true** (Hello gone); the live equivalent is Phase 0 (remove Space Invaders).
10. All 5 validation commands pass with zero errors → Phase 5.

## Priority-ordered tasks — Step 1 (Base System)

### Phase 0 — Remove Space Invaders (unblocks everything)
- [ ] Delete backend Space Invaders: overwrite `views/game.py` + `templates/game.html`
      (repurposed in Phase 4), remove `tests/test_game_view.py` SI assertions
      (retain the reusable `TestErrorHandlers` if present).
- [ ] Delete frontend engine: `frontend/src/game/*`, `frontend/src/islands/game/*`,
      `frontend/tests/game/*`, `e2e/game.spec.ts`.
- [ ] Drop `game` from the `main.ts` island registry (add `minesweeper` in Phase 4).
      Note: `frontend/src/types/index.ts` contains **no** SI types to remove — only the
      generic `IslandProps<T>` (keep as-is) and doc comments mentioning Space Invaders
      (refresh the comments when convenient; non-blocking).
- [ ] Fix stale `script/db-seed` (imports removed `Hello` model) — make it a no-op or seed a `Game`.
      Non-blocking (not in validation commands) but should not stay broken. Optionally refresh the
      stale `.github/skills/test-in-browser/SKILL.md` (Hello island / `/api/hello` docs).

### Phase 1 — Data layer (model + schemas + migration)
- [ ] `models/game.py` — `Game` model: `id`, `rows`, `cols`, `mine_count`,
      `mine_positions` (JSON `[[r,c],…]`, null until first reveal), `revealed` (JSON),
      `flags` (JSON), `status` (`playing`/`won`/`lost`), `started_at`,
      `first_move_at` (nullable), `ended_at` (nullable). Register in `models/__init__.py`.
- [ ] `schemas/game.py` — Pydantic v2 models `MoveRequest(row, col)`, `CellView(state, adjacent?, mine?)`,
      `GameStateView(gameId, rows, cols, mineCount, flagsUsed, status, board)`,
      plus the **redacting serializer** (unrevealed cells expose no `adjacent`/`mine`;
      `mine` only populated on loss). Export from `schemas/__init__.py`.
- [ ] Alembic migration creating `games`, chained `down_revision = 'f1a2b3c4d5e6'`.
      Verify `flask db upgrade` on a fresh DB.

### Phase 2 — Server-authoritative game logic (`controllers/minesweeper.py`)
- [ ] Named constants: `ROWS=9`, `COLS=9`, `MINE_COUNT=10` (keep as a preset-friendly
      shape so Step 2 generalizes without a rewrite).
- [ ] `place_mines(game, safe_row, safe_col)` — pick `mine_count` distinct cells
      excluding the safe cell **and its 8 neighbors**; store positions; set `first_move_at`.
      Only called on first reveal (first-click safety).
- [ ] `reveal(game, row, col)` — no-op if flagged/revealed or `status != playing`;
      place mines on first reveal; mine → `status = lost` + `ended_at`; else compute
      adjacency and **iterative** (stack/queue) flood-fill of zero-adjacency cells;
      then evaluate win.
- [ ] `toggle_flag(game, row, col)` — reject if revealed or `status != playing`;
      add/remove from `flags`; over-flagging allowed.
- [ ] `is_won(game)` — true when every non-mine cell revealed → `status = won` + `ended_at`.

### Phase 3 — JSON API (`views/api.py`, `url_prefix="/api"`)
- [ ] `POST /api/games` — create game (mines not placed yet), return redacted board (all hidden).
- [ ] `POST /api/games/<id>/reveal` — body `{row,col}`; on loss include full mine layout.
- [ ] `POST /api/games/<id>/flag` — body `{row,col}`; return board + `flagsUsed`.
- [ ] `GET /api/games/<id>` — return current redacted board + status (resume).
- [ ] Validate bodies with `MoveRequest.model_validate(...)` (catch `ValidationError`→400),
      404 on unknown `gameId`; every response through the redacting serializer.
      Register `api_bp` in `views/__init__.py`.
- [ ] **Error responses must be JSON.** `errors.py` only returns JSON when the request sends
      `Accept: application/json`, so either `return jsonify(error=...), 4xx` directly from the API
      handlers, or ensure `api.ts` always sends that header (do both for safety). Don't rely on bare
      `abort(404)` returning JSON — it renders HTML without the header.

### Phase 4 — Frontend island (`frontend/src/minesweeper/` + component)
- [ ] `types.ts` (`CellView`, `GameStateView`) + `api.ts` (`createGame`, `reveal`, `flag`, `getGame`).
- [ ] `Cell.tsx` (hidden/flagged/revealed-number/mine; left-click reveal, right-click
      flag, suppress context menu), `Board.tsx` (dimension-driven 9×9 grid),
      `Controls.tsx` (mine counter `mineCount − flagsUsed`, client timer starting on
      first reveal + stopping on end, new-game button).
- [ ] `useGame.ts` (holds `gameId` + `GameStateView`; `newGame`/`revealCell`/`flagCell`).
- [ ] `components/MinesweeperIsland.tsx` (composes Controls + Board; win/loss banner)
      + `islands/minesweeper/index.ts` (mount). Register `minesweeper` in `main.ts`.
- [ ] `views/game.py` + `templates/game.html` → `<div data-island="minesweeper">`,
      title "Minesweeper".

### Phase 5 — Tests + validation
- [ ] `tests/test_minesweeper_logic.py` — inject mine positions / seed RNG: mine count,
      first-click safety (incl. neighbors), flood-fill of contiguous zero region,
      win only when all safe cells revealed, loss on mine.
- [ ] `tests/test_api_game.py` — **redaction is the security test**: playing-game
      responses never contain mine/adjacency for unrevealed cells; create → all hidden;
      flag toggles; 404 bad id; 400 bad input.
- [ ] `tests/test_game_view.py` — `GET /` 200 + `data-island="minesweeper"`.
- [ ] `e2e/minesweeper.spec.ts` — load 9×9 + title; reveal starts timer; right-click
      flag updates counter; mine → lost; seeded win path.
- [ ] Run `script/setup`, `script/test`, `script/typecheck`, `script/lint`,
      `script/test-e2e` — fix all failures. (10 base acceptance criteria + all commands green.)

---

## Step 2 (Extension) — after Base is green (out of scope for the ultimate goal)
Difficulty presets (`DIFFICULTIES` map: beginner/intermediate/expert) threaded
through model/schema/create endpoint/selector; `Score` model + migration;
`controllers/leaderboard.py` with **server-authoritative** `seconds = ended_at −
first_move_at`; `GET/POST /api/leaderboard` (409 duplicate, 400/422 non-won);
`Leaderboard.tsx` + win-submission flow; `tests/test_presets.py` +
`tests/test_leaderboard.py`; extend E2E. See `specs/minesweeper-step2-extension.md`.

## Risks / watch-outs
- **Redaction leak** is the highest-risk defect — route all responses through one
  serializer and test it directly.
- **Flood-fill must be iterative** (explicit stack), per spec, to avoid recursion overflow.
- `vite build` empties `src/app/static/` (removes `.gitkeep`) — restore after local build.
- Run Playwright with `--reporter=list` in agent/CI shells (html reporter blocks).
