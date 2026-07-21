/**
 * Game state hook.
 *
 * Holds the current `gameId` + redacted `GameStateView`, the currently selected
 * `difficulty`, and exposes actions that post to the server and replace local
 * state with the server's authoritative response. The client never computes
 * board outcomes itself — it only renders what the server returns.
 */
import { useCallback, useState } from 'react'

import { createGame, flag as apiFlag, reveal as apiReveal } from './api'
import type { Difficulty, GameStateView } from './types'

export interface UseGame {
  state: GameStateView | null
  difficulty: Difficulty
  newGame: (difficulty: Difficulty) => Promise<void>
  revealCell: (row: number, col: number) => Promise<void>
  flagCell: (row: number, col: number) => Promise<void>
}

export function useGame(): UseGame {
  const [state, setState] = useState<GameStateView | null>(null)
  const [difficulty, setDifficulty] = useState<Difficulty>('beginner')

  const newGame = useCallback(async (next: Difficulty) => {
    // Track the chosen difficulty before the request so the UI (selector,
    // leaderboard) reflects the new level immediately, then adopt the server's
    // authoritative fresh state.
    setDifficulty(next)
    setState(await createGame(next))
  }, [])

  const revealCell = useCallback(
    async (row: number, col: number) => {
      if (!state || state.status !== 'playing') return
      setState(await apiReveal(state.gameId, row, col))
    },
    [state],
  )

  const flagCell = useCallback(
    async (row: number, col: number) => {
      if (!state || state.status !== 'playing') return
      setState(await apiFlag(state.gameId, row, col))
    },
    [state],
  )

  return { state, difficulty, newGame, revealCell, flagCell }
}
