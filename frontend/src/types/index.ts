/**
 * Shared TypeScript types for the application.
 *
 * These types are used across islands and components. Minesweeper-specific types
 * live in `frontend/src/minesweeper/types.ts` alongside the API client that
 * consumes them.
 */

/**
 * Props passed to islands via the `data-props` attribute.
 *
 * Each island receives its initial data from the server. The Minesweeper island
 * fetches its own state from `/api` and needs no server-embedded data, but the
 * type is kept generic so future islands can pass typed initial state.
 */
export type IslandProps<T = unknown> = {
  initialData?: T
}
