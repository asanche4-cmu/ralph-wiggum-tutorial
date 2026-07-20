# Feature: Minesweeper — Extension (Difficulty Presets + Persistent Leaderboard)

> **Assignment step:** Step 2 of 2 (Extension). This builds directly on the base system specified in `minesweeper-step1-base.md`, which must already be implemented and working (server-authoritative single-difficulty play).

## Feature Description
Extend the working base Minesweeper game with three classic difficulty presets and a **persistent leaderboard** of best completion times. Players choose a difficulty before starting, and on winning they can submit their name to a leaderboard that survives server restarts. Crucially, completion times are computed **authoritatively on the server** from stored timestamps — the client timer remains display-only — so the leaderboard cannot be gamed from the browser. All of this layers on top of the existing server-authoritative game engine without changing its core reveal/flag/win/loss logic.

## User Story
As a player of the Minesweeper game
I want to pick a difficulty and record my best times on a leaderboard
So that I can challenge myself at different levels and compete on completion time

## Problem Statement
The base system plays a single fixed difficulty and forgets every game the moment it ends. That's a complete game but a shallow one. Adding difficulty presets increases replay value, and a persistent leaderboard gives play a lasting purpose — while also exercising a second data model, additional API endpoints, server-side verification of results, and a new frontend surface. It's a self-contained, meaningful increment on top of the base.

## Solution Statement
Generalize the single hard-coded board into three presets, and add a leaderboard subsystem:
- Three difficulty presets: **Beginner** (9×9, 10 mines), **Intermediate** (16×16, 40 mines), **Expert** (16×30, 99 mines)
- A difficulty selector in the UI; `POST /api/games` now accepts a `difficulty`
- A persistent `Score` model and a leaderboard API (list top times per difficulty; submit a score)
- **Server-authoritative timing**: elapsed time is computed from `first_move_at`/`ended_at` on the server, not reported by the client
- Verification that a score can only be submitted for a game that the server recorded as `won`, and only once
- A leaderboard UI showing best times per difficulty, and a name-submission flow on win

The base engine's reveal, flag, flood-fill, and win/loss logic are reused unchanged; this step adds around them.

## Relevant Files
Use these files to implement the feature.

**Backend (modify)**
- `src/app/controllers/minesweeper.py` — Replace the single board constant with a `DIFFICULTIES` map; accept a difficulty when creating a game. Record the authoritative elapsed time on win.
- `src/app/models/game.py` — Add a `difficulty` column; ensure `first_move_at`/`ended_at` are populated (already present from base)
- `src/app/schemas/game.py` — Add `difficulty` to the create request and to `GameStateView`
- `src/app/views/api.py` — `POST /api/games` accepts `difficulty`; register the new leaderboard routes
- `src/app/models/__init__.py` — Add the `Score` import
- `src/app/__init__.py` — Register the leaderboard blueprint if separate

**Frontend (modify)**
- `frontend/src/minesweeper/types.ts` — Add `Difficulty` and `LeaderboardEntry` types; add `difficulty` to game types
- `frontend/src/minesweeper/api.ts` — `createGame` takes a difficulty; add `getLeaderboard`, `submitScore`
- `frontend/src/minesweeper/Controls.tsx` — Add the difficulty selector; sizing adapts per difficulty
- `frontend/src/minesweeper/Board.tsx` — Handle variable grid dimensions (already dimension-driven, verify Expert renders)
- `frontend/src/minesweeper/useGame.ts` — `newGame(difficulty)`; expose current difficulty
- `frontend/src/components/MinesweeperIsland.tsx` — Add win-time submission flow; mount the leaderboard

### New Files

**Backend**
- `src/app/models/score.py` — `Score` model: `id`, `game_id` (FK), `name`, `difficulty`, `seconds`, `created_at`
- `src/app/schemas/score.py` — `SubmitScoreRequest` (`gameId`, `name`), `LeaderboardEntry` (`name`, `seconds`, `createdAt`)
- `src/app/controllers/leaderboard.py` — `top_scores(difficulty, limit)`, `record_score(game_id, name)`
- `src/app/views/leaderboard.py` — Leaderboard API blueprint (or add routes to `views/api.py`)
- `migrations/` — New Alembic migration creating the `scores` table and adding `difficulty` to `games`
- `tests/test_leaderboard.py` — API tests for submission verification + listing
- `tests/test_presets.py` — Tests that each preset produces the correct dimensions/mine count

**Frontend**
- `frontend/src/minesweeper/Leaderboard.tsx` — Best-times table per difficulty
- `frontend/src/minesweeper/WinDialog.tsx` — Name-entry prompt shown on win (or inline in the island)

## API Contract (additions / changes)
Additions and changes relative to the base contract.

- `POST /api/games` — **Changed.** Body now `{ "difficulty": "beginner" | "intermediate" | "expert" }`. Unknown values return 400. Response `GameStateView` now includes `difficulty`.
- `GET /api/leaderboard?difficulty=beginner` — **New.** Returns the top N `{ name, seconds, createdAt }`, ascending by `seconds`.
- `POST /api/leaderboard` — **New.** Body `{ "gameId": ..., "name": ... }`. The server verifies the referenced game exists, has `status == "won"`, and has not already been recorded. It computes authoritative `seconds = ended_at - first_move_at`, inserts the score, and returns the updated leaderboard for that difficulty. Returns 409 if already recorded, 400/422 if the game is not won.

## Implementation Plan

### Phase 1: Difficulty Presets
Generalize the hard-coded board into a `DIFFICULTIES` map and thread a `difficulty` value through the model, schemas, create endpoint, and the frontend selector. At the end of this phase all three board sizes are playable end-to-end (still no leaderboard).

### Phase 2: Leaderboard Backend
Add the `Score` model, migration, schemas, and the leaderboard controller/endpoints, including server-side verification and authoritative time computation. Cover with tests before wiring the UI.

### Phase 3: Leaderboard Frontend & Polish
Add the leaderboard table and the win-time submission flow to the island. Verify Expert renders correctly, add E2E coverage, and run all validation commands.

## Step by Step Tasks

### Step 1: Introduce Difficulty Presets (Backend)
- In `controllers/minesweeper.py`, replace the single board constant with:
  - `beginner`: 9 rows × 9 cols, 10 mines
  - `intermediate`: 16 rows × 16 cols, 40 mines
  - `expert`: 16 rows × 30 cols, 99 mines
- Add validation that rejects unknown difficulty strings with a 400

### Step 2: Thread Difficulty Through Model & Schema
- Add a `difficulty` column to the `Game` model
- Add `difficulty` to the create-game request schema and to `GameStateView`
- Create an Alembic migration adding the `difficulty` column to `games`

### Step 3: Update the Create-Game Endpoint
- `POST /api/games` reads `difficulty` from the body, looks up the preset, and creates a game with the right `rows`/`cols`/`mine_count`
- Confirm reveal/flag/win/loss logic from the base works unchanged across all three sizes

### Step 4: Difficulty Selector (Frontend)
- Add `Difficulty` to `types.ts`; `createGame(difficulty)` in `api.ts`; `newGame(difficulty)` in `useGame.ts`
- Add a difficulty dropdown to `Controls.tsx`; selecting a value starts a new game at that difficulty
- Verify `Board.tsx` renders variable dimensions, including the wide Expert board

### Step 5: Create the Score Model & Migration
- Create `models/score.py`: `id`, `game_id` (FK to `games`), `name`, `difficulty`, `seconds`, `created_at`
- Register it in `models/__init__.py`
- Create an Alembic migration for the `scores` table

### Step 6: Create Score Schemas
- `schemas/score.py`: `SubmitScoreRequest` (`gameId`, `name`), `LeaderboardEntry` (`name`, `seconds`, `createdAt`)
- Enforce a reasonable name length; trim/sanitize whitespace

### Step 7: Implement the Leaderboard Controller
- `controllers/leaderboard.py`:
  - `top_scores(difficulty, limit)` → scores for that difficulty, ascending by `seconds`
  - `record_score(game_id, name)`:
    - Load the game; reject if it doesn't exist, isn't `won`, or already has a score
    - Compute `seconds` authoritatively from `ended_at - first_move_at`
    - Insert the `Score` and return the updated leaderboard

### Step 8: Add Leaderboard Endpoints
- `GET /api/leaderboard?difficulty=` → `top_scores`
- `POST /api/leaderboard` → `record_score`, with 409 for duplicates and 400/422 for non-won games
- Register the routes (in `views/api.py` or a new `views/leaderboard.py` blueprint)

### Step 9: Build the Leaderboard UI
- `Leaderboard.tsx`: fetches and displays top times for the currently selected difficulty; refreshes after a submission
- Add `getLeaderboard` and `submitScore` to `api.ts`

### Step 10: Win-Time Submission Flow
- In `MinesweeperIsland.tsx`, when `status` becomes `won`, prompt for a name (`WinDialog.tsx` or inline)
- Call `submitScore(gameId, name)`, then refresh the leaderboard for that difficulty
- Handle the already-recorded (409) case gracefully (e.g., disable re-submit)

### Step 11: Write Backend Tests
- `tests/test_presets.py`: each preset yields the correct dimensions and mine count; unknown difficulty is rejected
- `tests/test_leaderboard.py`:
  - Cannot submit for an unfinished or lost game
  - Cannot double-submit for the same game
  - `seconds` is derived from server timestamps, not client input
  - Listing returns entries sorted ascending by `seconds`, filtered by difficulty

### Step 12: Write/Extend E2E Test
- Extend `e2e/minesweeper.spec.ts`:
  - Selecting each difficulty starts a board of the correct dimensions
  - A seeded/deterministic win path prompts for a name and, after submission, shows the time on the leaderboard
  - The leaderboard filters by the selected difficulty

### Step 13: Run Validation Commands
- Run `script/test`, `script/typecheck`, `script/lint`, `script/test-e2e` and fix all failures

## Testing Strategy

### Unit / API Tests
- **Preset correctness** is simple and deterministic — assert dimensions and mine counts directly.
- **Leaderboard verification** is the important part: these are security-style tests ensuring a score can't be recorded for a game the server didn't mark `won`, can't be submitted twice, and that timing comes from the server. Inject or seed timestamps to assert exact `seconds`.

### Edge Cases
- Unknown difficulty string is rejected (400)
- Submitting a score for a `playing` or `lost` game is rejected
- Duplicate submission for the same `gameId` is rejected (409)
- Authoritative time ignores any client-provided duration
- Empty or overly long names are rejected or trimmed
- Leaderboard is correctly partitioned by difficulty (an Expert time never appears under Beginner)
- The wide Expert board (30 columns) renders and remains playable
- Leaderboard persists across a server restart (it's in the database, not memory)

## Acceptance Criteria
1. A difficulty selector offers Beginner (9×9/10), Intermediate (16×16/40), and Expert (16×30/99)
2. Selecting a difficulty starts a new server-generated board of the correct size
3. All base gameplay (reveal, flood-fill, flag, win/loss) works at every difficulty
4. On winning, the player can submit a name and their time is recorded
5. Completion time is computed authoritatively on the server from stored timestamps
6. A score can only be recorded for a game the server marked `won`, and only once
7. The leaderboard shows best times per difficulty, sorted ascending, filtered by difficulty
8. The leaderboard persists across server restarts
9. All validation commands pass with zero errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Apply the new migrations + ensure dependencies
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
- This step deliberately reuses the base engine unchanged. If implementing a preset requires editing reveal/flood-fill/win logic, that's a signal the base wasn't fully dimension-driven — fix it there rather than special-casing per difficulty.
- Keep timing server-authoritative: the client timer is for display only. The whole point of storing `first_move_at`/`ended_at` in the base was to make the leaderboard trustworthy here.
- The `game_id` foreign key on `Score` both prevents duplicate submissions and lets you verify the game's status at submission time.
- Good further extensions if you have time: a "chord" click (reveal neighbors of a satisfied number), a daily-seed challenge board, or per-player accounts — but none are required for this step.