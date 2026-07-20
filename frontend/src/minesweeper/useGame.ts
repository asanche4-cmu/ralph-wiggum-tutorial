/**
 * Game state hook.
 *
 * Holds the current `gameId` + redacted `GameStateView` and exposes actions that
 * post to the server and replace local state with the server's authoritative
 * response. The client never computes board outcomes itself — it only renders
 * what the server returns.
 */
import { useCallback, useState } from 'react'

import { createGame, flag as apiFlag, reveal as apiReveal } from './api'
import type { GameStateView } from './types'

export interface UseGame {
  state: GameStateView | null
  newGame: () => Promise<void>
  revealCell: (row: number, col: number) => Promise<void>
  flagCell: (row: number, col: number) => Promise<void>
}

export function useGame(): UseGame {
  const [state, setState] = useState<GameStateView | null>(null)

  const newGame = useCallback(async () => {
    setState(await createGame())
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

  return { state, newGame, revealCell, flagCell }
}
