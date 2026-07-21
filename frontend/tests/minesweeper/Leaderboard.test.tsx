/**
 * Unit tests for the Leaderboard component.
 *
 * The server owns ordering and the difficulty filter, so these tests verify the
 * component renders what the API returns and re-fetches when the difficulty
 * changes — the two behaviours the island relies on to keep the board in sync.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'

import { Leaderboard } from '@/minesweeper/Leaderboard'
import { getLeaderboard } from '@/minesweeper/api'
import type { Difficulty, LeaderboardView } from '@/minesweeper/types'

vi.mock('@/minesweeper/api', () => ({
  getLeaderboard: vi.fn(),
}))

const mockGetLeaderboard = vi.mocked(getLeaderboard)

function view(difficulty: Difficulty, entries: LeaderboardView['entries']): LeaderboardView {
  return { difficulty, entries }
}

describe('Leaderboard', () => {
  beforeEach(() => {
    mockGetLeaderboard.mockReset()
  })

  it('renders entries returned by the server', async () => {
    mockGetLeaderboard.mockResolvedValue(
      view('beginner', [
        { name: 'Ada', seconds: 12, createdAt: '2026-07-20T00:00:00' },
        { name: 'Grace', seconds: 30, createdAt: '2026-07-20T00:01:00' },
      ]),
    )

    render(<Leaderboard difficulty="beginner" />)

    await waitFor(() => expect(screen.getAllByTestId('leaderboard-row')).toHaveLength(2))
    expect(screen.getByText(/Ada/)).toBeInTheDocument()
    expect(screen.getByText('12s')).toBeInTheDocument()
    expect(mockGetLeaderboard).toHaveBeenCalledWith('beginner')
  })

  it('shows an empty state when there are no times', async () => {
    mockGetLeaderboard.mockResolvedValue(view('expert', []))
    render(<Leaderboard difficulty="expert" />)
    await waitFor(() => expect(screen.getByTestId('leaderboard-empty')).toBeInTheDocument())
  })

  it('re-fetches for the selected difficulty', async () => {
    mockGetLeaderboard.mockResolvedValue(view('intermediate', []))
    render(<Leaderboard difficulty="intermediate" />)
    await waitFor(() => expect(mockGetLeaderboard).toHaveBeenCalledWith('intermediate'))
  })
})
