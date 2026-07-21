import { test, expect } from '@playwright/test';

/**
 * E2E coverage for the Minesweeper homepage.
 *
 * These verify the server-authoritative game from the player's perspective:
 * the board renders at the right size, revealing starts the timer, right-click
 * flags a cell and updates the mine counter, and revealing cells eventually
 * ends the game with a banner. Outcomes are decided by the server; the client
 * only renders what it returns.
 */
test.describe('Minesweeper Page', () => {
  test('has the Minesweeper title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Minesweeper/i);
  });

  test('renders a 9x9 board with controls', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByTestId('board')).toBeVisible();
    await expect(page.locator('[data-testid^="cell-"]')).toHaveCount(81);
    await expect(page.getByTestId('mine-counter')).toHaveText('010');
    await expect(page.getByTestId('timer')).toBeVisible();
    await expect(page.getByTestId('new-game')).toBeVisible();
  });

  test('revealing a cell starts the timer', async ({ page }) => {
    await page.goto('/');

    await page.getByTestId('cell-4-4').click();
    await expect(page.locator('[data-state="revealed"]').first()).toBeVisible();

    // The client timer starts on the first reveal and should tick past 000.
    await expect
      .poll(async () => page.getByTestId('timer').textContent(), { timeout: 3000 })
      .not.toBe('000');
  });

  test('right-click flags a cell and updates the counter', async ({ page }) => {
    await page.goto('/');

    await page.getByTestId('cell-0-0').click({ button: 'right' });
    await expect(page.getByTestId('cell-0-0')).toHaveAttribute('data-state', 'flagged');
    await expect(page.getByTestId('mine-counter')).toHaveText('009');
  });

  test('revealing cells eventually ends the game', async ({ page }) => {
    await page.goto('/');

    // With 10 mines among 81 cells, clicking every cell in order deterministically
    // steps on a mine, ending the game as a loss (further clicks are no-ops).
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        await page
          .getByTestId(`cell-${r}-${c}`)
          .click({ force: true })
          .catch(() => {});
      }
    }

    await expect(page.getByTestId('status-banner')).toBeVisible();
  });

  // Step 2: difficulty presets. Selecting a difficulty starts a fresh
  // server-generated board of the matching size, proving the whole stack
  // (selector -> createGame(difficulty) -> preset lookup -> dimension-driven
  // render) works end-to-end, including the wide 30-column Expert board.
  const presets = [
    { difficulty: 'beginner', cells: 81 },
    { difficulty: 'intermediate', cells: 256 },
    { difficulty: 'expert', cells: 480 },
  ];
  for (const { difficulty, cells } of presets) {
    test(`selecting ${difficulty} renders a ${cells}-cell board`, async ({ page }) => {
      await page.goto('/');
      await expect(page.getByTestId('board')).toBeVisible();

      await page.getByTestId('difficulty').selectOption(difficulty);
      await expect(page.locator('[data-testid^="cell-"]')).toHaveCount(cells);
    });
  }

  // Step 2: the leaderboard is mounted and reflects the selected difficulty.
  // (Its populated ordering is covered by backend API tests; a deterministic
  // win can't be driven through the UI because mines are placed randomly on the
  // first click and there is no UI mine-injection path.)
  test('leaderboard is visible and follows the selected difficulty', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('leaderboard')).toBeVisible();
    await expect(page.getByTestId('leaderboard')).toHaveAttribute('data-difficulty', 'beginner');

    await page.getByTestId('difficulty').selectOption('expert');
    await expect(page.getByTestId('leaderboard')).toHaveAttribute('data-difficulty', 'expert');
  });
});
