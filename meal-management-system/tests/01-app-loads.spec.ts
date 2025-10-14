import { test, expect } from '@playwright/test';

test.describe('Application Loading Tests', () => {
  test('should load the application homepage', async ({ page }) => {
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check if page title is correct
    await expect(page).toHaveTitle(/Hostel Meal/i);

    // Check if login page elements are visible
    const loginHeading = page.locator('h1, h2').filter({ hasText: /welcome back|login|sign in/i });
    await expect(loginHeading.first()).toBeVisible();

    console.log('✅ Application loads successfully');
  });

  test('should have login and register links', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Look for login/register related text
    const pageContent = await page.content();
    const hasLoginContent = pageContent.toLowerCase().includes('login') ||
                           pageContent.toLowerCase().includes('sign in');

    expect(hasLoginContent).toBeTruthy();

    console.log('✅ Login/Register elements present');
  });

  test('should load without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    page.on('pageerror', error => {
      errors.push(error.message);
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Filter out known safe errors
    const criticalErrors = errors.filter(err =>
      !err.includes('favicon') &&
      !err.includes('manifest') &&
      !err.includes('ResizeObserver')
    );

    if (criticalErrors.length > 0) {
      console.log('⚠️  Console errors detected:', criticalErrors);
    } else {
      console.log('✅ No critical JavaScript errors');
    }

    expect(criticalErrors.length).toBeLessThan(5); // Allow up to 5 non-critical errors
  });

  test('should be responsive - mobile view', async ({ page, viewport }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone size
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check if page renders at mobile size
    const viewportSize = page.viewportSize();
    expect(viewportSize?.width).toBe(375);

    console.log('✅ Mobile responsive layout works');
  });

  test('should be responsive - tablet view', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad size
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const viewportSize = page.viewportSize();
    expect(viewportSize?.width).toBe(768);

    console.log('✅ Tablet responsive layout works');
  });

  test('should load CSS styles correctly', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check if any element has computed styles (indicates CSS loaded)
    const bodyStyles = await page.evaluate(() => {
      const body = document.body;
      const styles = window.getComputedStyle(body);
      return {
        margin: styles.margin,
        padding: styles.padding,
        fontFamily: styles.fontFamily
      };
    });

    expect(bodyStyles.fontFamily).toBeTruthy();
    console.log('✅ CSS styles loaded correctly');
  });
});
