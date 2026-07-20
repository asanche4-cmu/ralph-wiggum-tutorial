/**
 * A single Minesweeper cell.
 *
 * Renders the four visible states (hidden, flagged, revealed-number, mine) from
 * the server's redacted `CellView`. Left-click reveals; right-click toggles a
 * flag and suppresses the browser context menu (per the spec).
 */
import type { MouseEvent } from 'react'

import type { CellView } from './types'

interface CellProps {
  cell: CellView
  row: number
  col: number
  onReveal: (row: number, col: number) => void
  onFlag: (row: number, col: number) => void
}

// Classic Minesweeper number colors.
const NUMBER_COLORS: Record<number, string> = {
  1: 'text-blue-600',
  2: 'text-green-700',
  3: 'text-red-600',
  4: 'text-indigo-800',
  5: 'text-amber-700',
  6: 'text-teal-600',
  7: 'text-gray-900',
  8: 'text-gray-600',
}

const BASE =
  'w-8 h-8 flex items-center justify-center text-sm font-bold ' +
  'border border-gray-400 select-none'

export function Cell({ cell, row, col, onReveal, onFlag }: CellProps) {
  const testId = `cell-${row}-${col}`

  const handleContextMenu = (event: MouseEvent) => {
    // Suppress the browser menu so right-click means "flag".
    event.preventDefault()
    onFlag(row, col)
  }

  if (cell.state === 'revealed') {
    if (cell.mine) {
      return (
        <div data-testid={testId} data-state="mine" className={`${BASE} bg-red-300`}>
          💣
        </div>
      )
    }
    const n = cell.adjacent ?? 0
    return (
      <div
        data-testid={testId}
        data-state="revealed"
        className={`${BASE} bg-gray-100 ${n > 0 ? NUMBER_COLORS[n] : ''}`}
      >
        {n > 0 ? n : ''}
      </div>
    )
  }

  return (
    <button
      type="button"
      data-testid={testId}
      data-state={cell.state}
      onClick={() => onReveal(row, col)}
      onContextMenu={handleContextMenu}
      className={`${BASE} bg-gray-300 hover:bg-gray-400`}
    >
      {cell.state === 'flagged' ? '🚩' : ''}
    </button>
  )
}
