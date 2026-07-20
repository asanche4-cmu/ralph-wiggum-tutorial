/**
 * The Minesweeper grid.
 *
 * Purely dimension-driven: it lays out `rows × cols` cells from the server's
 * `GameStateView`, so the same component renders any difficulty (9×9 up to the
 * wide 16×30 Expert board introduced in Step 2) with no changes.
 */
import { Cell } from './Cell'
import type { GameStateView } from './types'

interface BoardProps {
  state: GameStateView
  onReveal: (row: number, col: number) => void
  onFlag: (row: number, col: number) => void
}

export function Board({ state, onReveal, onFlag }: BoardProps) {
  return (
    <div
      data-testid="board"
      className="inline-grid gap-px bg-gray-500 p-1 rounded"
      style={{ gridTemplateColumns: `repeat(${state.cols}, minmax(0, 2rem))` }}
    >
      {state.board.map((row, r) =>
        row.map((cell, c) => (
          <Cell
            key={`${r}-${c}`}
            cell={cell}
            row={r}
            col={c}
            onReveal={onReveal}
            onFlag={onFlag}
          />
        )),
      )}
    </div>
  )
}
