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
  rows: number
  cols: number
  mineCount: number
  flagsUsed: number
  status: GameStatus
  board: CellView[][]
}
