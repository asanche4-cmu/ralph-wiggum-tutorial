/**
 * Best-times leaderboard for a single difficulty.
 *
 * Fetches from the server whenever the selected `difficulty` changes or the
 * `refreshKey` bumps (the island bumps it after a successful submission). The
 * server owns the ordering (ascending by seconds) and the difficulty filter, so
 * this component just renders what it returns.
 */
import { useEffect, useState } from 'react'

import { getLeaderboard } from './api'
import type { Difficulty, LeaderboardEntry } from './types'

interface LeaderboardProps {
  difficulty: Difficulty
  /** Bump to force a re-fetch (e.g. after submitting a new score). */
  refreshKey?: number
}

export function Leaderboard({ difficulty, refreshKey = 0 }: LeaderboardProps) {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])

  useEffect(() => {
    let active = true
    getLeaderboard(difficulty)
      .then((view) => {
        if (active) setEntries(view.entries)
      })
      .catch(() => {
        if (active) setEntries([])
      })
    return () => {
      active = false
    }
  }, [difficulty, refreshKey])

  return (
    <div data-testid="leaderboard" data-difficulty={difficulty} className="mt-6 w-full max-w-xs">
      <h2 className="text-sm font-semibold text-gray-700 mb-2 text-center">
        Best Times — {difficulty}
      </h2>
      {entries.length === 0 ? (
        <p data-testid="leaderboard-empty" className="text-xs text-gray-500 text-center">
          No times yet. Win a game to get on the board!
        </p>
      ) : (
        <ol className="text-sm">
          {entries.map((entry, index) => (
            <li
              key={`${entry.name}-${entry.createdAt}-${index}`}
              data-testid="leaderboard-row"
              className="flex justify-between border-b border-gray-200 py-1 font-mono tabular-nums"
            >
              <span className="truncate mr-2">
                {index + 1}. {entry.name}
              </span>
              <span>{entry.seconds}s</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
