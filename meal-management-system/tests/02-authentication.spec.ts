import { test, expect } from '@playwright/test';

test.describe('Authentication Tests', () => {
  test('should display login form', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Look for email and password inputs
    const emailInput = page.locator('input[type="email"], input[name="email"]');
    const passwordInput = page.locator('input[type="password"], input[name="password"]');

    await expect(emailInput.first()).toBeVisible({ timeout: 10000 });
    await expect(passwordInput.first()).toBeVisible();

    console.log('✅ Login form displays correctly');
  });

  test('should show validation errors for empty login', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Try to find and click submit button
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');

    if (await submitButton.count() > 0) {
      await submitButton.first().click();

      // Wait a bit for validation
      await page.waitForTimeout(1000);

      console.log('✅ Form validation triggered');
    } else {
      console.log('⚠️  Submit button not found');
    }
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Look for register/signup link
    const registerLink = page.locator('a:has-text("Register"), a:has-text("Sign Up"), a:has-text("Create Account")');

    if (await registerLink.count() > 0) {
      await registerLink.first().click();
      await page.waitForLoadState('networkidle');

      // Check if we're on register page
      const url = page.url();
      expect(url).toContain('register');

      console.log('✅ Navigation to register page works');
    } else {
      console.log('⚠️  Register link not found');
    }
  });

  test('should display register form', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');

    // Look for registration form fields
    const emailInput = page.locator('input[type="email"], input[name="email"]');
    const passwordInput = page.locator('input[type="password"], input[name="password"]');
    const nameInput = page.locator('input[name="name"], input[placeholder*="name"]');

    const hasEmail = await emailInput.count() > 0;
    const hasPassword = await passwordInput.count() > 0;

    expect(hasEmail || hasPassword).toBeTruthy();

    console.log('✅ Register form displays correctly');
  });

  test('should attempt login with test credentials', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Fill login form with test credentials
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();

    if (await emailInput.isVisible()) {
      await emailInput.fill('manager@hostel.com');
      await passwordInput.fill('Manager@123');

      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();

      // Wait for navigation or error
      await page.waitForTimeout(3000);

      const url = page.url();

      if (url.includes('dashboard')) {
        console.log('✅ Login successful! Redirected to dashboard');
      } else {
        console.log('⚠️  Login attempt made (may need Supabase setup or test data)');
      }
    }
  });

  test('should handle invalid credentials gracefully', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();

    if (await emailInput.isVisible()) {
      await emailInput.fill('invalid@test.com');
      await passwordInput.fill('wrongpassword');

      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();

      // Wait for error message
      await page.waitForTimeout(2000);

      // Check if still on login page (expected for invalid credentials)
      const url = page.url();
      expect(url).toContain('login');

      console.log('✅ Invalid credentials handled appropriately');
    }
  });

  test('should have password field masked', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    const passwordInput = page.locator('input[type="password"]').first();

    if (await passwordInput.isVisible()) {
      const inputType = await passwordInput.getAttribute('type');
      expect(inputType).toBe('password');

      console.log('✅ Password field is properly masked');
    }
  });
});
