# Feature: Minesweeper — Base System (Server-Authoritative Play)

> **Assignment step:** Step 1 of 2 (Base System). The extension (difficulty presets + persistent leaderboard) is specified separately in `minesweeper-step2-extension.md` and builds directly on this.

## Feature Description
A single-difficulty Minesweeper game served as the homepage of the application. The mine layout is generated and stored **on the server**, never sent to the browser until the game ends — so the board cannot be cheated by inspecting client state. The browser renders the grid and sends each reveal/flag action to the server, which validates the move, performs flood-fill for empty cells, computes adjacent-mine counts, and returns only the cells the player is allowed to see. This base system uses one fixed difficulty (Beginner, 9×9, 10 mines) and has no persistence beyond the in-progress game. It replaces the existing Hello World demo entirely and is delivered as an island within the Flask + React Islands architecture.

## User Story
As a visitor to the application
I want to play a game of Minesweeper in my browser
So that I can enjoy a classic puzzle where the game logic is fair and server-verified

## Problem Statement
The current homepage displays a basic Hello World CRUD demo that has served its purpose as a tutorial scaffold. We need to replace it with Minesweeper. Unlike a purely client-side arcade game, Minesweeper is a natural fit for demonstrating a real interactive backend: the server owns the hidden game state and validates every move. This base step establishes that server-authoritative foundation — models, schemas, an API, migrations, and a rendering frontend — with the smallest scope that is still a complete, playable game.

## Solution Statement
Build a server-authoritative Minesweeper game at a single difficulty. The Flask backend owns all secret state and exposes a small JSON API; the React Islands frontend renders the visible board and issues actions. This step includes:
- One fixed difficulty: **Beginner** (9×9, 10 mines)
- Server-side board generation with **first-click safety** (the first revealed cell is never a mine)
- Server-side reveal logic including recursive/iterative flood-fill of zero-adjacency cells
- Server-side flagging, win detection (all non-mine cells revealed), and loss detection (a mine revealed)
- Game states surfaced to the client: `playing`, `won`, `lost`
- A client-side timer and mine counter for display, plus a "new game" button

There is **no** leaderboard, **no** difficulty selector, and **no** persistence of finished games in this step — those are the extension.

The existing Hello World model, API routes, controller, schema, frontend components, and tests will be removed.

## Relevant Files
Use these files to implement the feature:

**Backend (modify/remove)**
- `src/app/views/hello.py` — Remove
- `src/app/controllers/hello.py` — Remove entirely
- `src/app/models/hello.py` — Remove entirely
- `src/app/schemas/hello.py` — Remove entirely
- `src/app/models/__init__.py` — Remove Hello import; add Game import
- `src/app/templates/base.html` — Update to mount the minesweeper island
- `src/app/__init__.py` — Update blueprint registration for the game + api blueprints

**Frontend (modify/remove)**
- `frontend/src/islands/hello/index.ts` — Remove
- `frontend/src/components/HelloIsland.tsx` — Remove
- `frontend/src/types/index.ts` — Replace Hello types with game/API types
- `frontend/src/main.ts` — Update island registry

**Tests (remove/replace)**
- `tests/` — Remove Hello-related tests
- `e2e/hello.spec.ts` — Remove

### New Files

**Backend**
- `src/app/models/game.py` — `Game` model: hidden board, revealed/flagged sets, status, timing
- `src/app/schemas/game.py` — Schemas for game create, move requests, and the **redacted** client-facing board view
- `src/app/controllers/minesweeper.py` — Core game logic: board generation, first-click safety, reveal + flood-fill, flag toggle, win/loss evaluation
- `src/app/views/game.py` — Blueprint rendering the game page
- `src/app/views/api.py` — JSON API blueprint (create game, reveal, flag, get state)
- `src/app/templates/game.html` — Template extending base with the island mount point
- `migrations/` — New Alembic migration creating the `games` table (and dropping `hellos`)
- `tests/test_minesweeper_logic.py` — Unit tests for board generation, flood-fill, win/loss
- `tests/test_api_game.py` — API tests for create/reveal/flag/state and redaction
- `tests/test_game_view.py` — Test that `GET /` renders the island mount

**Frontend**
- `frontend/src/minesweeper/types.ts` — Shared types (`CellView`, `GameStateView`)
- `frontend/src/minesweeper/api.ts` — Typed fetch wrappers for the API endpoints
- `frontend/src/minesweeper/Board.tsx` — Renders the grid from the server's redacted view
- `frontend/src/minesweeper/Cell.tsx` — A single cell (hidden, flagged, revealed-number, mine)
- `frontend/src/minesweeper/Controls.tsx` — Mine counter, timer, new-game button
- `frontend/src/minesweeper/useGame.ts` — Hook holding game id + view state, dispatching reveal/flag
- `frontend/src/components/MinesweeperIsland.tsx` — Island root wiring Controls + Board
- `frontend/src/islands/minesweeper/index.ts` — Island registration entry point
- `e2e/minesweeper.spec.ts` — E2E test for load, reveal, flag, win/loss

## API Contract
All endpoints return JSON. The board view returned to the client **never** includes mine positions for unrevealed cells.

- `POST /api/games` — No body required (single difficulty). Creates a game (mines *not* placed yet — see first-click safety). Returns `{ gameId, rows, cols, mineCount, status, board }` where `board` is a grid of redacted `CellView`s (all `hidden`).
- `POST /api/games/<gameId>/reveal` — Body `{ "row": int, "col": int }`. On the first reveal, the server places mines avoiding the clicked cell and its neighbors, then reveals. Performs flood-fill for zero-adjacency cells. Returns the updated redacted board and `status`; if `status == "lost"`, also returns the full mine layout so the client can show where mines were.
- `POST /api/games/<gameId>/flag` — Body `{ "row": int, "col": int }`. Toggles a flag. Rejected if the cell is already revealed. Returns updated board + `flagsUsed`.
- `GET /api/games/<gameId>` — Returns the current redacted board + status (for reload/resume).

## Implementation Plan

### Phase 1: Foundation — Remove Hello World & Establish Data Layer
Remove the Hello World feature entirely. Create the `Game` model, its schemas, and an Alembic migration. Register the new blueprints. At the end of this phase the app boots, the DB has the `games` table, and `GET /` renders an empty island mount.

### Phase 2: Core Backend — Server-Authoritative Game Logic
Implement board generation with first-click safety, the reveal algorithm with flood-fill, flag toggling, and win/loss evaluation in `controllers/minesweeper.py`. Wire these into the API blueprint. Cover the logic with unit tests before touching the UI, since this is the part that must be correct and cheat-proof.

### Phase 3: Frontend — Island, Render, Play
Build the React island (Controls, Board, Cell) against the typed API client. Implement the client timer and mine counter and the new-game button. Wire the island into `main.ts` and the template. Add E2E tests and run all validation commands.

## Step by Step Tasks

### Step 1: Remove Hello World (Backend + Frontend)
- Delete `controllers/hello.py`, `models/hello.py`, `schemas/hello.py`, `views/hello.py`
- Remove Hello imports from `models/__init__.py` and blueprint registration from `__init__.py`
- Delete Hello-related tests in `tests/` and `e2e/hello.spec.ts`
- Delete `frontend/src/islands/hello/index.ts` and `frontend/src/components/HelloIsland.tsx`; remove Hello types from `frontend/src/types/index.ts`

### Step 2: Define Board Constants
- Define the single preset in `controllers/minesweeper.py`: 9 rows × 9 cols, 10 mines
- Keep these as named constants so the extension can generalize them into presets later without rewriting the logic

### Step 3: Create the Game Model
- Create `models/game.py` with a `Game` SQLAlchemy model:
  - `id`, `rows`, `cols`, `mine_count`
  - `mine_positions` (server-only JSON list of `[row, col]`; populated on first reveal)
  - `revealed` (JSON/set of revealed cells), `flags` (JSON/set of flagged cells)
  - `status` (`playing` / `won` / `lost`)
  - `started_at`, `first_move_at` (nullable), `ended_at` (nullable)
- Register it in `models/__init__.py`

### Step 4: Create Schemas
- `schemas/game.py`:
  - `MoveRequest` (`row`, `col`)
  - `CellView` (`state`: `hidden` | `flagged` | `revealed`; `adjacent`: int | null; `mine`: bool | null — only set on loss)
  - `GameStateView` (`gameId`, `rows`, `cols`, `mineCount`, `flagsUsed`, `status`, `board`)
- Add a serializer that produces the **redacted** `GameStateView` — unrevealed cells must expose no mine or adjacency info

### Step 5: Create the Alembic Migration
- Generate a migration creating the `games` table and dropping `hellos`
- Verify the migration applies cleanly on a fresh DB (`script/setup`)

### Step 6: Implement Board Generation with First-Click Safety
- Implement `place_mines(game, safe_row, safe_col)`:
  - Randomly select `mine_count` distinct cells, **excluding** the safe cell and its 8 neighbors
  - Store positions on the game; set `first_move_at`
- Do **not** place mines at game creation — only on the first reveal, so the first click is always safe

### Step 7: Implement Reveal + Flood-Fill
- Implement `reveal(game, row, col)`:
  - No-op if the cell is flagged or already revealed, or if `status != playing`
  - If first reveal, call `place_mines` first
  - If the cell is a mine → mark revealed, set `status = lost`, set `ended_at`
  - Else compute adjacent mine count; if 0, flood-fill all 8 neighbors, stopping at numbered cells
  - Use an explicit stack/queue (not recursion) so large empty regions don't overflow
  - After revealing, evaluate win (Step 9)

### Step 8: Implement Flag Toggle
- Implement `toggle_flag(game, row, col)`:
  - Reject if the cell is already revealed or `status != playing`
  - Add/remove the cell from `flags`; track `flagsUsed` for the client counter
  - Over-flagging (more flags than mines) is allowed

### Step 9: Implement Win/Loss Evaluation
- `is_won(game)` → true when every non-mine cell is revealed
- On win: set `status = won`, `ended_at`
- On loss (mine revealed): set `status = lost`, `ended_at`; the reveal response includes the full mine layout so the UI can render the exploded board

### Step 10: Build the API Blueprint
- Create `views/api.py` implementing the four endpoints from the API Contract
- Validate request bodies against schemas; return 400 on bad input, 404 for unknown `gameId`
- Every game-state response goes through the redacting serializer
- Register the blueprint at `url_prefix="/api"`

### Step 11: Build the Game View + Template
- Create `views/game.py` blueprint: `GET /` renders `game.html`
- Create `templates/game.html` extending `base.html` with `<div data-island="minesweeper"></div>` and title "Minesweeper"
- Register the blueprint at `url_prefix="/"`

### Step 12: Build the Frontend API Client and Types
- Create `frontend/src/minesweeper/types.ts` mirroring the server schemas
- Create `frontend/src/minesweeper/api.ts` with typed functions: `createGame`, `reveal`, `flag`, `getGame`

### Step 13: Build the Board, Cell, and Controls Components
- `Cell.tsx`: renders hidden / flagged / revealed(number) / mine states; left-click reveals, right-click flags — suppress the browser context menu
- `Board.tsx`: renders the 9×9 grid from `GameStateView.board`
- `Controls.tsx`: remaining-mine counter (`mineCount - flagsUsed`), client-side timer (starts on first reveal, stops on win/loss), new-game button

### Step 14: Build the useGame Hook and Island Root
- `useGame.ts`: holds `gameId` and `GameStateView`; exposes `newGame()`, `revealCell`, `flagCell`; updates state from each API response
- `MinesweeperIsland.tsx`: composes Controls + Board; shows a win/loss banner based on `status`
- Create `frontend/src/islands/minesweeper/index.ts` exporting the island registration
- Update `frontend/src/main.ts`: remove the hello island, add the minesweeper island

### Step 15: Write Backend Tests
- `tests/test_minesweeper_logic.py`: mine count matches the preset; first click never a mine; flood-fill reveals contiguous zero regions; win only when all safe cells revealed; loss on mine reveal
- `tests/test_api_game.py`: create returns a redacted board with all cells hidden; reveal never leaks unrevealed mines; flag toggles; 404 on bad id; 400 on bad input
- `tests/test_game_view.py`: `GET /` returns 200 and contains `data-island="minesweeper"`

### Step 16: Write E2E Test
- `e2e/minesweeper.spec.ts`:
  - Page loads with a 9×9 grid visible and title "Minesweeper"
  - Left-clicking a cell reveals it (and the timer starts)
  - Right-clicking toggles a flag and updates the mine counter
  - Revealing a mine shows the lost state; a seeded scenario reaches a win

### Step 17: Run Validation Commands
- Run `script/test`, `script/typecheck`, `script/lint`, `script/test-e2e` and fix all failures

## Testing Strategy

### Unit Tests
- **Backend logic** is the priority: board generation, first-click safety, flood-fill correctness, and win/loss are deterministic and highly testable. Seed the RNG or inject mine positions in tests to make outcomes reproducible.
- **API redaction** is a security-style test: assert that responses for `playing` games never contain mine data for unrevealed cells.
- **Frontend** unit tests are optional; E2E gives better coverage for the interactive grid.

### Edge Cases
- First click is always safe, including its 8 neighbors
- Flood-fill terminates and does not overflow on large empty regions
- Flagging a revealed cell, or moving after game over, is rejected server-side
- Revealing an already-revealed or flagged cell is a no-op
- Right-click does not open the browser context menu
- Reloading the page can resume via `GET /api/games/<id>` (or cleanly starts a new game)
- Over-flagging is allowed and does not break win detection

## Acceptance Criteria
1. Visiting `/` displays a 9×9 Minesweeper board with a mine counter, timer, and new-game button
2. Mine positions are generated and stored server-side and are never present in API responses for unrevealed cells
3. The first revealed cell is never a mine
4. Left-click reveals a cell; revealing an empty (zero) cell flood-fills the contiguous region
5. Right-click toggles a flag and updates the remaining-mine counter
6. Revealing a mine ends the game as a loss and shows all mines
7. Revealing all non-mine cells ends the game as a win
8. The new-game button starts a fresh board
9. All existing Hello World code is fully removed
10. All validation commands pass with zero errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Ensure dependencies + database are set up
script/setup

# Run backend + frontend unit tests
script/test

# Run TypeScript and Python type checking
script/typecheck

# Run linting
script/lint

# Run E2E tests (auto-starts dev server)
script/test-e2e
```

## Notes
- The defining property of this design is **server authority**: the browser is a thin renderer that only ever knows what the server has revealed. This is what makes the backend genuinely interactive and cheat-resistant, and it's the main thing distinguishing this from a pure client-side arcade game.
- Store the hidden board (`mine_positions`, `revealed`, `flags`) as JSON columns for simplicity, or as related rows if you prefer normalized tables — either satisfies the spec.
- Keep board dimensions and mine count as named constants. The extension generalizes them into three presets, so isolating them now avoids a rewrite.
- Seed the RNG in tests (inject mine positions) so flood-fill and win/loss outcomes are deterministic.
- The client timer is display-only in this step; the extension introduces authoritative server-side timing for the leaderboard.