/**
 * Unit tests for the Cell component.
 *
 * Cell is where the redacted server view becomes DOM and where the two input
 * gestures (left-click reveal, right-click flag) are wired, so these cover the
 * spec's interaction rules directly — including that right-click must suppress
 * the browser context menu.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

import { Cell } from '@/minesweeper/Cell'

describe('Cell', () => {
  it('renders a hidden cell as a button', () => {
    render(<Cell cell={{ state: 'hidden' }} row={0} col={0} onReveal={() => {}} onFlag={() => {}} />)
    expect(screen.getByTestId('cell-0-0')).toHaveAttribute('data-state', 'hidden')
  })

  it('left-click reveals the cell', () => {
    const onReveal = vi.fn()
    render(<Cell cell={{ state: 'hidden' }} row={1} col={2} onReveal={onReveal} onFlag={() => {}} />)
    fireEvent.click(screen.getByTestId('cell-1-2'))
    expect(onReveal).toHaveBeenCalledWith(1, 2)
  })

  it('right-click flags the cell and suppresses the context menu', () => {
    const onFlag = vi.fn()
    render(<Cell cell={{ state: 'hidden' }} row={0} col={0} onReveal={() => {}} onFlag={onFlag} />)
    const event = fireEvent.contextMenu(screen.getByTestId('cell-0-0'))
    expect(onFlag).toHaveBeenCalledWith(0, 0)
    // fireEvent returns false when preventDefault() was called on the event.
    expect(event).toBe(false)
  })

  it('renders the adjacent-mine count when revealed', () => {
    render(<Cell cell={{ state: 'revealed', adjacent: 3 }} row={0} col={0} onReveal={() => {}} onFlag={() => {}} />)
    expect(screen.getByTestId('cell-0-0')).toHaveTextContent('3')
  })

  it('renders a mine once the game is lost', () => {
    render(<Cell cell={{ state: 'revealed', mine: true }} row={0} col={0} onReveal={() => {}} onFlag={() => {}} />)
    expect(screen.getByTestId('cell-0-0')).toHaveAttribute('data-state', 'mine')
  })
})
