/**
 * Name-entry prompt shown on a win so the player can record their time.
 *
 * Purely presentational: it collects a name and delegates submission to the
 * island. It reflects the three post-win states — awaiting entry, submitting,
 * and recorded (including the already-recorded 409 case) — so the player always
 * knows whether their time made it onto the board.
 */
import { useState } from 'react'

interface WinDialogProps {
  seconds: number
  submitting: boolean
  recorded: boolean
  error: string | null
  onSubmit: (name: string) => void
}

export function WinDialog({ seconds, submitting, recorded, error, onSubmit }: WinDialogProps) {
  const [name, setName] = useState('')

  if (recorded) {
    return (
      <div data-testid="win-recorded" className="mt-4 text-center text-green-800">
        Your time of {seconds}s is on the leaderboard! 🏆
      </div>
    )
  }

  return (
    <form
      data-testid="win-dialog"
      className="mt-4 flex flex-col items-center gap-2"
      onSubmit={(e) => {
        e.preventDefault()
        const trimmed = name.trim()
        if (trimmed) onSubmit(trimmed)
      }}
    >
      <p className="text-sm text-green-800">You won in {seconds}s! Enter your name:</p>
      <div className="flex gap-2">
        <input
          data-testid="win-name"
          aria-label="Your name"
          value={name}
          maxLength={20}
          onChange={(e) => setName(e.target.value)}
          disabled={submitting}
          className="border border-gray-400 rounded px-2 py-1 text-sm"
        />
        <button
          type="submit"
          data-testid="win-submit"
          disabled={submitting || name.trim().length === 0}
          className="bg-green-600 text-white rounded px-3 py-1 text-sm disabled:opacity-50"
        >
          {submitting ? 'Saving…' : 'Submit'}
        </button>
      </div>
      {error && (
        <p data-testid="win-error" className="text-xs text-red-600">
          {error}
        </p>
      )}
    </form>
  )
}
