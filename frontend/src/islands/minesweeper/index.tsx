/**
 * Minesweeper island mount logic.
 *
 * Dynamically imported by `main.ts` when a `[data-island="minesweeper"]`
 * element is found. The board fetches its own state from `/api`, so no
 * server-provided props are needed; the signature stays uniform with the island
 * contract so the registry can treat all islands identically.
 */
import { createRoot } from 'react-dom/client'

import { MinesweeperIsland } from '@/components/MinesweeperIsland'

export function mount(element: HTMLElement, _props: unknown): void {
  // Clear the server-rendered fallback (e.g. the <noscript> notice).
  element.innerHTML = ''

  const root = createRoot(element)
  root.render(<MinesweeperIsland />)
}
