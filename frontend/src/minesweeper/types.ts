/**
 * Shared Minesweeper types.
 *
 * These mirror the server's Pydantic schemas (`src/app/schemas/game.py`) exactly
 * — this file is the single place the client's view of the wire format lives, so
 * Board/Cell/Controls/useGame all agree on shape. The server redacts hidden
 * cells, so `adjacent`/`mine` are optional and only present when the server
 * chose to reveal them.
 */

export type CellState = 'hidden' | 'flagged' | 'revealed'

export type GameStatus = 'playing' | 'won' | 'lost'

/** The three difficulty presets. Must match the server's `DIFFICULTIES` keys. */
export type Difficulty = 'beginner' | 'intermediate' | 'expert'

/** Ordered list + labels for rendering the difficulty selector. */
export const DIFFICULTIES: { value: Difficulty; label: string }[] = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'expert', label: 'Expert' },
]

/** The client-visible view of a single cell (already redacted by the server). */
export interface CellView {
  state: CellState
  /** Adjacent-mine count; present only for revealed non-mine cells. */
  adjacent?: number
  /** True only for mine cells once the game is lost. */
  mine?: boolean
}

/** The full redacted game state returned by every API endpoint. */
export interface GameStateView {
  gameId: number
  difficulty: Difficulty
  rows: number
  cols: number
  mineCount: number
  flagsUsed: number
  status: GameStatus
  board: CellView[][]
}

/** One leaderboard row (mirrors the server's `LeaderboardEntry`). */
export interface LeaderboardEntry {
  name: string
  seconds: number
  createdAt: string
}

/** The leaderboard for a single difficulty (mirrors `LeaderboardView`). */
export interface LeaderboardView {
  difficulty: Difficulty
  entries: LeaderboardEntry[]
}
