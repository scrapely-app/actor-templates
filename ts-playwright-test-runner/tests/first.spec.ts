import { expect, test } from '@playwright/test';

test('has appropriate size', async ({ page }) => {
    let totalDownloaded = 0;

    page.on('response', (r) => {
        r.body()
            .then((b) => {
                totalDownloaded += b.byteLength;
            })
            .catch(() => {
                // Ignore errors.
            });
    });

    await page.goto('https://crawlee.dev/', { waitUntil: 'networkidle' });

    // Expect the total amount of data to be less than 10 MB.
    expect(totalDownloaded).toBeLessThan(10 * 1024 * 1024);
});
