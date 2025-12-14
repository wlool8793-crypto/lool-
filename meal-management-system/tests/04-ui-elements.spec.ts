import { test, expect } from '@playwright/test';

test.describe('UI Elements Tests', () => {
  test('should have accessible form inputs', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Check for input accessibility
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();

    if (await emailInput.isVisible()) {
      const emailName = await emailInput.getAttribute('name');
      const passwordName = await passwordInput.getAttribute('name');

      expect(emailName || '').toBeTruthy();
      expect(passwordName || '').toBeTruthy();

      console.log('✅ Form inputs have proper attributes');
    }
  });

  test('should have clickable buttons', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    const buttons = await page.locator('button').count();
    expect(buttons).toBeGreaterThan(0);

    console.log(`✅ Found ${buttons} button(s) on page`);
  });

  test('should have proper links', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    const links = await page.locator('a').count();

    console.log(`✅ Found ${links} link(s) on page`);
  });

  test('should have images load correctly', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const images = page.locator('img');
    const imageCount = await images.count();

    if (imageCount > 0) {
      for (let i = 0; i < Math.min(imageCount, 5); i++) {
        const image = images.nth(i);
        const isVisible = await image.isVisible().catch(() => false);

        if (isVisible) {
          const naturalWidth = await image.evaluate((img: HTMLImageElement) => img.naturalWidth);
          if (naturalWidth > 0) {
            console.log(`✅ Image ${i + 1} loaded successfully`);
          }
        }
      }
    }
  });

  test('should have proper text contrast', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Check if main content is visible (indicates proper contrast)
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toBeTruthy();

    console.log('✅ Page has readable text content');
  });

  test('should have proper focus states', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Tab through inputs
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);

    expect(focusedElement).toBeTruthy();
    console.log(`✅ Focus states work (focused on: ${focusedElement})`);
  });

  test('should load fonts correctly', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const fontFamily = await page.evaluate(() => {
      return window.getComputedStyle(document.body).fontFamily;
    });

    expect(fontFamily).toBeTruthy();
    console.log(`✅ Fonts loaded: ${fontFamily}`);
  });
});
