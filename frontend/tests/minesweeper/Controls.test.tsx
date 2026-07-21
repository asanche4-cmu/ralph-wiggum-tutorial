/**
 * Unit tests for the Controls component.
 *
 * The remaining-mine counter (mineCount − flagsUsed) is player-facing state
 * derived from the server response, so it is worth pinning down — including the
 * over-flagging case where it goes negative (which the server permits). Step 2
 * adds the difficulty selector: choosing a level must request a new game at that
 * difficulty without the parent having to translate the event.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

import { Controls } from '@/minesweeper/Controls'

function renderControls(overrides = {}) {
  const props = {
    mineCount: 10,
    flagsUsed: 0,
    seconds: 0,
    status: 'playing' as const,
    difficulty: 'beginner' as const,
    onDifficultyChange: vi.fn(),
    onNewGame: vi.fn(),
    ...overrides,
  }
  render(<Controls {...props} />)
  return props
}

describe('Controls', () => {
  it('shows remaining mines as mineCount minus flagsUsed', () => {
    renderControls({ flagsUsed: 3 })
    expect(screen.getByTestId('mine-counter')).toHaveTextContent('007')
  })

  it('shows a negative counter when over-flagged', () => {
    renderControls({ flagsUsed: 12 })
    expect(screen.getByTestId('mine-counter')).toHaveTextContent('-02')
  })

  it('renders the timer value', () => {
    renderControls({ seconds: 42 })
    expect(screen.getByTestId('timer')).toHaveTextContent('042')
  })

  it('fires onNewGame when the face button is clicked', () => {
    const { onNewGame } = renderControls({ status: 'won' as const })
    fireEvent.click(screen.getByTestId('new-game'))
    expect(onNewGame).toHaveBeenCalledTimes(1)
  })

  it('reflects the current difficulty and reports changes', () => {
    const { onDifficultyChange } = renderControls({ difficulty: 'beginner' as const })
    const select = screen.getByTestId('difficulty') as HTMLSelectElement
    expect(select.value).toBe('beginner')

    fireEvent.change(select, { target: { value: 'expert' } })
    expect(onDifficultyChange).toHaveBeenCalledWith('expert')
  })
})
