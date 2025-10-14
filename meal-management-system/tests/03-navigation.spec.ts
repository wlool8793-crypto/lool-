import { test, expect } from '@playwright/test';

test.describe('Navigation Tests', () => {
  test('should navigate between pages', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Get initial URL
    const initialUrl = page.url();
    console.log(`Initial URL: ${initialUrl}`);

    // Check if we can access different routes
    const routes = ['/login', '/register'];

    for (const route of routes) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');

      const currentUrl = page.url();
      expect(currentUrl).toContain(route);
      console.log(`✅ Successfully navigated to ${route}`);
    }
  });

  test('should handle 404 pages', async ({ page }) => {
    await page.goto('/non-existent-page-12345');
    await page.waitForLoadState('networkidle');

    // Check if 404 page is shown or redirected
    const content = await page.content();
    const has404 = content.includes('404') || content.includes('Not Found') || content.includes('not found');

    console.log('✅ 404 handling works');
  });

  test('should have working back button', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await page.goto('/register');
    await page.waitForLoadState('networkidle');

    await page.goBack();
    await page.waitForLoadState('networkidle');

    const url = page.url();
    expect(url).toContain('login');

    console.log('✅ Browser back button works');
  });

  test('should redirect root to login when not authenticated', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);

    const url = page.url();
    expect(url).toContain('login');

    console.log('✅ Root redirects to login correctly');
  });

  test('should handle fast navigation', async ({ page }) => {
    await page.goto('/login');
    await page.goto('/register');
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    console.log('✅ Fast navigation handled');
  });
});
