import { test, expect } from '@playwright/test';

test.describe('CV Creation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the CV maker application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('complete CV creation workflow', async ({ page }) => {
    // Step 1: Personal Information
    await test.step('Fill in personal information', async () => {
      await page.fill('input[placeholder*="Full Name"]', 'John Doe');
      await page.fill('input[placeholder*="Email"]', 'john.doe@example.com');
      await page.fill('input[placeholder*="Phone"]', '+1 (555) 123-4567');
      await page.fill('input[placeholder*="Address"]', '123 Main St, City, State 12345');
      await page.fill('input[placeholder*="LinkedIn"]', 'https://linkedin.com/in/johndoe');
      await page.fill('input[placeholder*="Website"]', 'https://johndoe.com');
      await page.fill('input[placeholder*="GitHub"]', 'https://github.com/johndoe');

      // Click next button
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Professional Summary', { state: 'visible' });
    });

    // Step 2: Professional Summary
    await test.step('Fill in professional summary', async () => {
      await page.fill('textarea[placeholder*="professional summary"]',
        'Experienced software developer with 5+ years in full-stack development. ' +
        'Passionate about creating user-friendly applications and solving complex problems. ' +
        'Strong background in React, Node.js, and cloud technologies.'
      );

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Work Experience', { state: 'visible' });
    });

    // Step 3: Work Experience
    await test.step('Add work experience', async () => {
      // Add first work experience
      await page.click('button:has-text("Add Experience")');
      await page.fill('input[placeholder*="Job Title"]', 'Senior Software Engineer');
      await page.fill('input[placeholder*="Company"]', 'Tech Corp');
      await page.fill('input[placeholder*="Location"]', 'San Francisco, CA');
      await page.fill('input[placeholder*="Start Date"]', '2020-01-01');
      await page.fill('input[placeholder*="End Date"]', '2023-01-01');
      await page.fill('textarea[placeholder*="Description"]',
        'Led development of scalable web applications serving 1M+ users. ' +
        'Mentored junior developers and improved team productivity by 40%.'
      );

      // Add achievement
      await page.click('button:has-text("Add Achievement")');
      await page.fill('input[placeholder*="Achievement"]', 'Reduced application load time by 60%');

      await page.click('button:has-text("Save")');
      await page.waitForSelector('text=Senior Software Engineer', { state: 'visible' });

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Education', { state: 'visible' });
    });

    // Step 4: Education
    await test.step('Add education', async () => {
      await page.click('button:has-text("Add Education")');
      await page.fill('input[placeholder*="Degree"]', 'Bachelor of Science in Computer Science');
      await page.fill('input[placeholder*="Field of Study"]', 'Computer Science');
      await page.fill('input[placeholder*="Institution"]', 'University of Technology');
      await page.fill('input[placeholder*="Location"]', 'City, State');
      await page.fill('input[placeholder*="Graduation Date"]', '2019-05-01');
      await page.fill('input[placeholder*="GPA"]', '3.8');

      await page.click('button:has-text("Save")');
      await page.waitForSelector('text=Bachelor of Science', { state: 'visible' });

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Skills', { state: 'visible' });
    });

    // Step 5: Skills
    await test.step('Add skills', async () => {
      const skills = [
        { name: 'JavaScript', level: 'Advanced' },
        { name: 'React', level: 'Advanced' },
        { name: 'Node.js', level: 'Advanced' },
        { name: 'TypeScript', level: 'Intermediate' },
        { name: 'Python', level: 'Intermediate' },
        { name: 'AWS', level: 'Intermediate' },
        { name: 'Docker', level: 'Intermediate' },
        { name: 'MongoDB', level: 'Intermediate' },
      ];

      for (const skill of skills) {
        await page.click('button:has-text("Add Skill")');
        await page.fill('input[placeholder*="Skill Name"]', skill.name);
        await page.selectOption('select:has-text("Level")', skill.level);
        await page.click('button:has-text("Save")');
        await page.waitForSelector(`text=${skill.name}`, { state: 'visible' });
      }

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Projects', { state: 'visible' });
    });

    // Step 6: Projects
    await test.step('Add projects', async () => {
      await page.click('button:has-text("Add Project")');
      await page.fill('input[placeholder*="Project Name"]', 'E-commerce Platform');
      await page.fill('textarea[placeholder*="Description"]',
        'Full-stack e-commerce solution with real-time inventory management and payment processing.'
      );
      await page.fill('input[placeholder*="Technologies"]', 'React, Node.js, MongoDB, Stripe');
      await page.fill('input[placeholder*="Project URL"]', 'https://ecommerce-demo.com');
      await page.fill('input[placeholder*="Start Date"]', '2022-01-01');
      await page.fill('input[placeholder*="End Date"]', '2022-06-01');

      await page.click('button:has-text("Save")');
      await page.waitForSelector('text=E-commerce Platform', { state: 'visible' });

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Preview', { state: 'visible' });
    });

    // Step 7: Preview and Generate PDF
    await test.step('Preview CV and generate PDF', async () => {
      // Wait for preview to load
      await page.waitForSelector('[data-testid="cv-preview"]', { state: 'visible' });

      // Verify all sections are present in preview
      await expect(page.locator('text=John Doe')).toBeVisible();
      await expect(page.locator('text=Senior Software Engineer')).toBeVisible();
      await expect(page.locator('text=Bachelor of Science')).toBeVisible();
      await expect(page.locator('text=JavaScript')).toBeVisible();
      await expect(page.locator('text=E-commerce Platform')).toBeVisible();

      // Test template switching
      await page.click('button:has-text("Change Template")');
      await page.click('text=Creative Template');
      await page.waitForSelector('[data-testid="cv-preview"]', { state: 'visible' });

      // Generate PDF
      await page.click('button:has-text("Generate PDF")');

      // Wait for PDF generation to complete
      await page.waitForSelector('text=PDF generated successfully', { state: 'visible', timeout: 30000 });

      // Download PDF
      await page.click('button:has-text("Download PDF")');

      // Verify download (this would need to be adapted based on actual download behavior)
      await expect(page.locator('text=Download started')).toBeVisible({ timeout: 10000 });
    });

    // Step 8: Save and Share
    await test.step('Save and share CV', async () => {
      // Save CV
      await page.click('button:has-text("Save CV")');
      await page.waitForSelector('text=CV saved successfully', { state: 'visible' });

      // Test sharing functionality
      await page.click('button:has-text("Share CV")');
      await page.waitForSelector('[data-testid="share-modal"]', { state: 'visible' });

      // Copy share link
      await page.click('button:has-text("Copy Link")');
      await expect(page.locator('text=Link copied to clipboard')).toBeVisible();

      // Close share modal
      await page.click('button[aria-label="Close"]');
    });
  });

  test('form validation and error handling', async ({ page }) => {
    await test.step('Test form validation', async () => {
      // Try to submit empty personal info form
      await page.click('button:has-text("Next")');

      // Check for validation errors
      await expect(page.locator('text=Full name is required')).toBeVisible();
      await expect(page.locator('text=Email is required')).toBeVisible();
      await expect(page.locator('text=Phone number is required')).toBeVisible();
      await expect(page.locator('text=Address is required')).toBeVisible();

      // Test invalid email
      await page.fill('input[placeholder*="Email"]', 'invalid-email');
      await page.click('button:has-text("Next")');
      await expect(page.locator('text=Invalid email address')).toBeVisible();

      // Test valid email
      await page.fill('input[placeholder*="Email"]', 'valid@example.com');
      await page.click('button:has-text("Next")');
      await expect(page.locator('text=Invalid email address')).not.toBeVisible();
    });
  });

  test('template switching and customization', async ({ page }) => {
    await test.step('Test template switching', async () => {
      // Fill in minimal required data
      await page.fill('input[placeholder*="Full Name"]', 'Test User');
      await page.fill('input[placeholder*="Email"]', 'test@example.com');
      await page.fill('input[placeholder*="Phone"]', '+1 (555) 123-4567');
      await page.fill('input[placeholder*="Address"]', '123 Test St');

      // Navigate to preview
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Professional Summary', { state: 'visible' });
      await page.fill('textarea[placeholder*="professional summary"]', 'Test summary');
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Work Experience', { state: 'visible' });
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Education', { state: 'visible' });
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Skills', { state: 'visible' });
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Projects', { state: 'visible' });
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Preview', { state: 'visible' });

      // Test different templates
      const templates = ['Modern Template', 'Traditional Template', 'Creative Template', 'Minimal Template'];

      for (const template of templates) {
        await page.click('button:has-text("Change Template")');
        await page.click(`text=${template}`);
        await page.waitForSelector('[data-testid="cv-preview"]', { state: 'visible' });
        await expect(page.locator('text=Test User')).toBeVisible();
      }
    });
  });

  test('accessibility features', async ({ page }) => {
    await test.step('Test accessibility features', async () => {
      // Test keyboard navigation
      await page.keyboard.press('Tab');
      await expect(page.locator('input[placeholder*="Full Name"]')).toBeFocused();

      await page.keyboard.press('Tab');
      await expect(page.locator('input[placeholder*="Email"]')).toBeFocused();

      // Test screen reader attributes
      await expect(page.locator('input[placeholder*="Full Name"]')).toHaveAttribute('aria-label');
      await expect(page.locator('input[placeholder*="Email"]')).toHaveAttribute('aria-label');

      // Test high contrast mode (if implemented)
      // This would depend on the actual implementation
    });
  });

  test('mobile responsiveness', async ({ page }) => {
    await test.step('Test mobile responsiveness', async () => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Test form layout on mobile
      await expect(page.locator('input[placeholder*="Full Name"]')).toBeVisible();
      await expect(page.locator('button:has-text("Next")')).toBeVisible();

      // Fill form on mobile
      await page.fill('input[placeholder*="Full Name"]', 'Mobile User');
      await page.fill('input[placeholder*="Email"]', 'mobile@example.com');

      // Test mobile navigation
      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Professional Summary', { state: 'visible' });

      // Reset to desktop viewport
      await page.setViewportSize({ width: 1280, height: 720 });
    });
  });

  test('performance and load testing', async ({ page }) => {
    await test.step('Test performance', async () => {
      // Measure initial load time
      const startTime = Date.now();
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      console.log(`Page load time: ${loadTime}ms`);
      expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds

      // Test form response time
      const formStartTime = Date.now();
      await page.fill('input[placeholder*="Full Name"]', 'Performance Test');
      const formResponseTime = Date.now() - formStartTime;
      console.log(`Form response time: ${formResponseTime}ms`);
      expect(formResponseTime).toBeLessThan(100); // Should respond within 100ms
    });
  });

  test('cross-browser compatibility', async ({ page }) => {
    await test.step('Test basic functionality across browsers', async () => {
      // This test will run on different browsers configured in playwright.config.ts
      await expect(page.locator('input[placeholder*="Full Name"]')).toBeVisible();
      await expect(page.locator('button:has-text("Next")')).toBeVisible();

      // Basic form interaction
      await page.fill('input[placeholder*="Full Name"]', 'Cross-browser Test');
      await page.fill('input[placeholder*="Email"]', 'test@example.com');
      await expect(page.locator('input[placeholder*="Full Name"]')).toHaveValue('Cross-browser Test');
    });
  });

  test('error recovery and edge cases', async ({ page }) => {
    await test.step('Test error recovery', async () => {
      // Test network error simulation
      await page.route('**/api/**', route => route.abort('failed'));

      // Try to save (should fail gracefully)
      await page.click('button:has-text("Save CV")');
      await page.waitForSelector('text=Failed to save CV', { state: 'visible', timeout: 10000 });

      // Retry after network recovery
      await page.unroute('**/api/**');
      await page.click('button:has-text("Retry")');
      await page.waitForSelector('text=CV saved successfully', { state: 'visible', timeout: 10000 });
    });
  });
});