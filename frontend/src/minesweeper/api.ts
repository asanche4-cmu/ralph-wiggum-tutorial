/**
 * Typed fetch client for the server-authoritative Minesweeper API.
 *
 * The single place the frontend talks to `/api`. Every request advertises
 * `Accept: application/json` so error responses come back as JSON (the shared
 * Flask error handlers content-negotiate), and every response is a redacted
 * `GameStateView`.
 */
import type { GameStateView } from './types'

interface RequestOptions {
  method: 'GET' | 'POST'
  body?: string
}

async function request(url: string, options: RequestOptions): Promise<GameStateView> {
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
  return response.json() as Promise<GameStateView>
}

/** Create a fresh game (mines are placed server-side on the first reveal). */
export function createGame(): Promise<GameStateView> {
  return request('/api/games', { method: 'POST' })
}

/** Reveal a cell. On loss the response includes the full mine layout. */
export function reveal(gameId: number, row: number, col: number): Promise<GameStateView> {
  return request(`/api/games/${gameId}/reveal`, {
    method: 'POST',
    body: JSON.stringify({ row, col }),
  })
}

/** Toggle a flag on a cell. */
export function flag(gameId: number, row: number, col: number): Promise<GameStateView> {
  return request(`/api/games/${gameId}/flag`, {
    method: 'POST',
    body: JSON.stringify({ row, col }),
  })
}

/** Fetch current state (for reload/resume). */
export function getGame(gameId: number): Promise<GameStateView> {
  return request(`/api/games/${gameId}`, { method: 'GET' })
}
