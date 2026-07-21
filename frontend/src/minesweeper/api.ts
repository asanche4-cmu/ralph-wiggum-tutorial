/**
 * Typed fetch client for the server-authoritative Minesweeper API.
 *
 * The single place the frontend talks to `/api`. Every request advertises
 * `Accept: application/json` so error responses come back as JSON (the shared
 * Flask error handlers content-negotiate), and every response is a redacted
 * `GameStateView`.
 */
import type { Difficulty, GameStateView, LeaderboardView } from './types'

interface RequestOptions {
  method: 'GET' | 'POST'
  body?: string
}

async function request<T>(url: string, options: RequestOptions): Promise<T> {
  const response = await fetch(url, {
    method: options.method,
    body: options.body,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) {
    throw new Error(`Minesweeper API request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

/**
 * Thrown when a score submission is rejected because the game was already
 * recorded (HTTP 409). Callers use this to disable re-submission gracefully
 * rather than surfacing a generic error.
 */
export class AlreadyRecordedError extends Error {
  constructor(message = 'Score already recorded for this game') {
    super(message)
    this.name = 'AlreadyRecordedError'
  }
}

/**
 * Create a fresh game at the given difficulty (default Beginner). Mines are
 * placed server-side on the first reveal.
 */
export function createGame(difficulty: Difficulty = 'beginner'): Promise<GameStateView> {
  return request<GameStateView>('/api/games', {
    method: 'POST',
    body: JSON.stringify({ difficulty }),
  })
}

/** Reveal a cell. On loss the response includes the full mine layout. */
export function reveal(gameId: number, row: number, col: number): Promise<GameStateView> {
  return request<GameStateView>(`/api/games/${gameId}/reveal`, {
    method: 'POST',
    body: JSON.stringify({ row, col }),
  })
}

/** Toggle a flag on a cell. */
export function flag(gameId: number, row: number, col: number): Promise<GameStateView> {
  return request<GameStateView>(`/api/games/${gameId}/flag`, {
    method: 'POST',
    body: JSON.stringify({ row, col }),
  })
}

/** Fetch current state (for reload/resume). */
export function getGame(gameId: number): Promise<GameStateView> {
  return request<GameStateView>(`/api/games/${gameId}`, { method: 'GET' })
}

/** Fetch the top times for a difficulty, ascending by seconds. */
export function getLeaderboard(difficulty: Difficulty): Promise<LeaderboardView> {
  return request<LeaderboardView>(`/api/leaderboard?difficulty=${difficulty}`, {
    method: 'GET',
  })
}

/**
 * Submit a name for a won game. The server computes the time authoritatively
 * from stored timestamps, so no duration is sent. Rejects with
 * {@link AlreadyRecordedError} if the game was already scored (409).
 */
export async function submitScore(gameId: number, name: string): Promise<LeaderboardView> {
  const response = await fetch('/api/leaderboard', {
    method: 'POST',
    body: JSON.stringify({ gameId, name }),
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
  })
  if (response.status === 409) {
    throw new AlreadyRecordedError()
  }
  if (!response.ok) {
    throw new Error(`Minesweeper API request failed: ${response.status}`)
  }
  return response.json() as Promise<LeaderboardView>
}
