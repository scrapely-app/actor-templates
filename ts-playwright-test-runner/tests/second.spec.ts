import { expect, test } from '@playwright/test';

test('has title', async ({ page }) => {
    await page.goto('https://crawlee.dev/');
    // Expect a title "to contain" a substring.
    await expect(page).toHaveTitle(/Crawlee/);
});

test('get started link', async ({ page }) => {
    await page.goto('https://crawlee.dev/js');
    // Click the first get started link.
    await page.getByRole('link', { name: 'Get started' }).first().click();
    // Expects the URL to contain quick-start.
    await expect(page).toHaveURL(/.*quick-start/);
});
