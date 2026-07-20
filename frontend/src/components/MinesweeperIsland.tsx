/**
 * Minesweeper island root.
 *
 * Composes Controls + Board over the `useGame` hook, owns the display-only
 * client timer, and shows a win/loss banner. It starts a game on mount and
 * renders whatever redacted state the server returns — all game outcomes are
 * decided server-side.
 */
import { useEffect, useMemo, useState } from 'react'

import { Board } from '@/minesweeper/Board'
import { Controls } from '@/minesweeper/Controls'
import { useGame } from '@/minesweeper/useGame'

export function MinesweeperIsland() {
  const { state, newGame, revealCell, flagCell } = useGame()
  const [seconds, setSeconds] = useState(0)

  // Start a game as soon as the island mounts.
  useEffect(() => {
    void newGame()
  }, [newGame])

  // Reset the timer whenever a fresh game begins.
  useEffect(() => {
    setSeconds(0)
  }, [state?.gameId])

  // The timer runs once the first cell is revealed and stops when the game ends.
  const running = useMemo(() => {
    if (!state || state.status !== 'playing') return false
    return state.board.some((row) => row.some((cell) => cell.state === 'revealed'))
  }, [state])

  useEffect(() => {
    if (!running) return
    const id = window.setInterval(() => setSeconds((s) => s + 1), 1000)
    return () => window.clearInterval(id)
  }, [running])

  if (!state) {
    return <p className="text-gray-600">Loading…</p>
  }

  return (
    <div className="flex flex-col items-center">
      <Controls
        mineCount={state.mineCount}
        flagsUsed={state.flagsUsed}
        seconds={seconds}
        status={state.status}
        onNewGame={() => void newGame()}
      />

      <Board state={state} onReveal={revealCell} onFlag={flagCell} />

      {state.status !== 'playing' && (
        <div
          data-testid="status-banner"
          data-status={state.status}
          className={`mt-4 px-4 py-2 rounded font-semibold ${
            state.status === 'won'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {state.status === 'won' ? 'You win! 🎉' : 'Game over 💥'}
        </div>
      )}
    </div>
  )
}
