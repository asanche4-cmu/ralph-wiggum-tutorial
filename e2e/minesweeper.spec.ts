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
});
