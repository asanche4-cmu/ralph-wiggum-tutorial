/**
 * Board controls: remaining-mine counter, timer, and new-game button.
 *
 * The counter shows `mineCount − flagsUsed` (it can go negative when the player
 * over-flags, which the server allows). The timer value is display-only and is
 * driven by the island; Step 2 introduces authoritative server-side timing for
 * the leaderboard.
 */
interface ControlsProps {
  mineCount: number
  flagsUsed: number
  seconds: number
  status: 'playing' | 'won' | 'lost'
  onNewGame: () => void
}

function threeDigits(value: number): string {
  const clamped = Math.max(-99, Math.min(999, value))
  const sign = clamped < 0 ? '-' : ''
  return sign + String(Math.abs(clamped)).padStart(sign ? 2 : 3, '0')
}

export function Controls({ mineCount, flagsUsed, seconds, status, onNewGame }: ControlsProps) {
  const remaining = mineCount - flagsUsed
  const face = status === 'won' ? '😎' : status === 'lost' ? '😵' : '🙂'

  return (
    <div className="flex items-center justify-between w-full mb-3 gap-4">
      <div
        data-testid="mine-counter"
        className="font-mono text-lg bg-black text-red-500 px-2 py-1 rounded tabular-nums"
      >
        {threeDigits(remaining)}
      </div>
      <button
        type="button"
        data-testid="new-game"
        onClick={onNewGame}
        aria-label="New game"
        className="text-2xl leading-none hover:scale-110 transition-transform"
      >
        {face}
      </button>
      <div
        data-testid="timer"
        className="font-mono text-lg bg-black text-red-500 px-2 py-1 rounded tabular-nums"
      >
        {threeDigits(seconds)}
      </div>
    </div>
  )
}
