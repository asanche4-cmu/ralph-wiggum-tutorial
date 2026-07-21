/**
 * Minesweeper island root.
 *
 * Composes the difficulty selector + Controls + Board + Leaderboard over the
 * `useGame` hook, owns the display-only client timer, and shows a win/loss
 * banner. On a win it prompts for a name and submits an authoritative score;
 * the leaderboard refreshes afterwards. All game outcomes and the recorded time
 * are decided server-side — the client only renders what the server returns.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'

import { AlreadyRecordedError, submitScore } from '@/minesweeper/api'
import { Board } from '@/minesweeper/Board'
import { Controls } from '@/minesweeper/Controls'
import { Leaderboard } from '@/minesweeper/Leaderboard'
import { WinDialog } from '@/minesweeper/WinDialog'
import { useGame } from '@/minesweeper/useGame'
import type { Difficulty } from '@/minesweeper/types'

export function MinesweeperIsland() {
  const { state, difficulty, newGame, revealCell, flagCell } = useGame()
  const [seconds, setSeconds] = useState(0)

  // Win-submission state. Reset whenever a new game starts (keyed on gameId).
  const [submitting, setSubmitting] = useState(false)
  const [recorded, setRecorded] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [leaderboardVersion, setLeaderboardVersion] = useState(0)

  // Start a Beginner game as soon as the island mounts (keeps the base default).
  useEffect(() => {
    void newGame('beginner')
  }, [newGame])

  // Reset the timer and submission state whenever a fresh game begins.
  useEffect(() => {
    setSeconds(0)
    setSubmitting(false)
    setRecorded(false)
    setSubmitError(null)
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

  const handleDifficultyChange = useCallback(
    (next: Difficulty) => {
      void newGame(next)
    },
    [newGame],
  )

  const handleSubmit = useCallback(
    async (name: string) => {
      if (!state) return
      setSubmitting(true)
      setSubmitError(null)
      try {
        await submitScore(state.gameId, name)
        setRecorded(true)
        setLeaderboardVersion((v) => v + 1)
      } catch (err) {
        if (err instanceof AlreadyRecordedError) {
          // Already on the board — treat as success so re-submit is disabled.
          setRecorded(true)
          setLeaderboardVersion((v) => v + 1)
        } else {
          setSubmitError('Could not submit your score. Please try again.')
        }
      } finally {
        setSubmitting(false)
      }
    },
    [state],
  )

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
        difficulty={difficulty}
        onDifficultyChange={handleDifficultyChange}
        onNewGame={() => void newGame(difficulty)}
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

      {state.status === 'won' && (
        <WinDialog
          seconds={seconds}
          submitting={submitting}
          recorded={recorded}
          error={submitError}
          onSubmit={handleSubmit}
        />
      )}

      <Leaderboard difficulty={difficulty} refreshKey={leaderboardVersion} />
    </div>
  )
}
