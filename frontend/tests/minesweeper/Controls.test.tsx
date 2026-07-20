/**
 * Unit tests for the Controls component.
 *
 * The remaining-mine counter (mineCount − flagsUsed) is player-facing state
 * derived from the server response, so it is worth pinning down — including the
 * over-flagging case where it goes negative (which the server permits).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

import { Controls } from '@/minesweeper/Controls'

describe('Controls', () => {
  it('shows remaining mines as mineCount minus flagsUsed', () => {
    render(<Controls mineCount={10} flagsUsed={3} seconds={0} status="playing" onNewGame={() => {}} />)
    expect(screen.getByTestId('mine-counter')).toHaveTextContent('007')
  })

  it('shows a negative counter when over-flagged', () => {
    render(<Controls mineCount={10} flagsUsed={12} seconds={0} status="playing" onNewGame={() => {}} />)
    expect(screen.getByTestId('mine-counter')).toHaveTextContent('-02')
  })

  it('renders the timer value', () => {
    render(<Controls mineCount={10} flagsUsed={0} seconds={42} status="playing" onNewGame={() => {}} />)
    expect(screen.getByTestId('timer')).toHaveTextContent('042')
  })

  it('fires onNewGame when the face button is clicked', () => {
    const onNewGame = vi.fn()
    render(<Controls mineCount={10} flagsUsed={0} seconds={0} status="won" onNewGame={onNewGame} />)
    fireEvent.click(screen.getByTestId('new-game'))
    expect(onNewGame).toHaveBeenCalledTimes(1)
  })
})
