import { test, expect } from '@playwright/test';

test.describe('Marriage Biodata Creation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the CV maker application
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Switch to marriage biodata mode
    await page.click('button:has-text("Marriage Biodata")');
    await page.waitForSelector('text=Create Marriage Biodata', { state: 'visible' });
  });

  test('complete marriage biodata creation workflow', async ({ page }) => {
    // Step 1: Personal Information
    await test.step('Fill in personal information', async () => {
      await page.fill('input[placeholder*="Full Name"]', 'Priya Sharma');
      await page.selectOption('select:has-text("Gender")', 'Female');
      await page.fill('input[placeholder*="Date of Birth"]', '1995-05-15');
      await page.fill('input[placeholder*="Height"]', '5\'4"');
      await page.fill('input[placeholder*="Weight"]', '55 kg');
      await page.selectOption('select:has-text("Blood Group")', 'B+');
      await page.selectOption('select:has-text("Marital Status")', 'Never Married');
      await page.fill('input[placeholder*="Mother Tongue"]', 'Hindi');
      await page.selectOption('select:has-text("Religion")', 'Hindu');
      await page.selectOption('select:has-text("Caste")', 'General');
      await page.fill('input[placeholder*="Complexion"]', 'Fair');
      await page.selectOption('select:has-text("Body Type")', 'Slim');
      await page.fill('textarea[placeholder*="Physical Description"]',
        'Slim and fair complexion with attractive features. Maintains good health through regular exercise.'
      );

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Contact Information', { state: 'visible' });
    });

    // Step 2: Contact Information
    await test.step('Fill in contact information', async () => {
      await page.fill('input[placeholder*="Email"]', 'priya.sharma@email.com');
      await page.fill('input[placeholder*="Phone"]', '+91 98765 43210');
      await page.fill('input[placeholder*="WhatsApp"]', '+91 98765 43210');
      await page.fill('input[placeholder*="Address"]', '123, Park Avenue, Mumbai, Maharashtra 400001');
      await page.fill('input[placeholder*="City"]', 'Mumbai');
      await page.fill('input[placeholder*="State"]', 'Maharashtra');
      await page.fill('input[placeholder*="Country"]', 'India');
      await page.fill('input[placeholder*="PIN Code"]', '400001');

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Family Information', { state: 'visible' });
    });

    // Step 3: Family Information
    await test.step('Fill in family information', async () => {
      await page.selectOption('select:has-text("Family Type")', 'Joint Family');
      await page.selectOption('select:has-text("Family Values")', 'Traditional');
      await page.selectOption('select:has-text("Family Status")', 'Middle Class');
      await page.fill('input[placeholder*="Father\'s Occupation"]', 'Government Officer');
      await page.fill('input[placeholder*="Mother\'s Occupation"]', 'Homemaker');
      await page.fill('input[placeholder*="Number of Brothers"]', '1');
      await page.fill('input[placeholder*="Number of Sisters"]', '1');
      await page.fill('input[placeholder*="Brothers Married"]', '0');
      await page.fill('input[placeholder*="Sisters Married"]', '0');
      await page.fill('textarea[placeholder*="Family Background"]',
        'Respectable family with traditional values. Father is a government officer and mother is a homemaker. ' +
        'Have one younger brother and one younger sister, both unmarried.'
      );

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Education', { state: 'visible' });
    });

    // Step 4: Education
    await test.step('Add education details', async () => {
      // Add Bachelor's degree
      await page.click('button:has-text("Add Education")');
      await page.fill('input[placeholder*="Degree"]', 'Bachelor of Engineering');
      await page.fill('input[placeholder*="Field of Study"]', 'Computer Science');
      await page.fill('input[placeholder*="Institution"]', 'Mumbai University');
      await page.fill('input[placeholder*="Year of Passing"]', '2017');
      await page.fill('input[placeholder*="Percentage/CGPA"]', '8.5 CGPA');
      await page.click('button:has-text("Save")');

      await page.waitForSelector('text=Bachelor of Engineering', { state: 'visible' });

      // Add Master's degree
      await page.click('button:has-text("Add Education")');
      await page.fill('input[placeholder*="Degree"]', 'Master of Business Administration');
      await page.fill('input[placeholder*="Field of Study"]', 'Finance');
      await page.fill('input[placeholder*="Institution"]', 'IIM Ahmedabad');
      await page.fill('input[placeholder*="Year of Passing"]', '2019');
      await page.fill('input[placeholder*="Percentage/CGPA"]', '7.8 CGPA');
      await page.click('button:has-text("Save")');

      await page.waitForSelector('text=Master of Business Administration', { state: 'visible' });

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Occupation', { state: 'visible' });
    });

    // Step 5: Occupation
    await test.step('Fill in occupation details', async () => {
      await page.fill('input[placeholder*="Current Designation"]', 'Senior Business Analyst');
      await page.fill('input[placeholder*="Company Name"]', 'Tech Solutions Pvt Ltd');
      await page.fill('input[placeholder*="Industry"]', 'Information Technology');
      await page.fill('input[placeholder*="Work Location"]', 'Mumbai');
      await page.fill('input[placeholder*="Annual Income"]', '12 Lakhs');
      await page.fill('textarea[placeholder*="Job Description"]',
        'Senior Business Analyst with 4+ years of experience in IT industry. ' +
        'Specialized in data analysis and business process optimization.'
      );

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Lifestyle', { state: 'visible' });
    });

    // Step 6: Lifestyle
    await test.step('Fill in lifestyle details', async () => {
      await page.selectOption('select:has-text("Eating Habits")', 'Vegetarian');
      await page.selectOption('select:has-text("Drinking Habits")', 'Never');
      await page.selectOption('select:has-text("Smoking Habits")', 'Never');
      await page.fill('input[placeholder*="Hobbies"]', 'Reading, Cooking, Traveling, Yoga');
      await page.fill('textarea[placeholder*="Interests"]',
        'Enjoy reading fiction and non-fiction books, love cooking different cuisines, ' +
        'passionate about traveling to new places, practice yoga regularly for fitness.'
      );

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Partner Preference', { state: 'visible' });
    });

    // Step 7: Partner Preference
    await test.step('Fill in partner preference', async () => {
      await page.selectOption('select:has-text("Preferred Age Range")', '28-35');
      await page.selectOption('select:has-text("Preferred Height")', '5\'7" - 6\'0"');
      await page.selectOption('select:has-text("Preferred Marital Status")', 'Never Married');
      await page.selectOption('select:has-text("Preferred Religion"]', 'Hindu');
      await page.selectOption('select:has-text("Preferred Caste"]', 'Doesn\'t Matter');
      await page.selectOption('select:has-text("Preferred Education"]', 'Post Graduate');
      await page.selectOption('select:has-text("Preferred Occupation"]', 'Professional');
      await page.fill('input[placeholder*="Preferred Location"]', 'Mumbai, Pune, Bangalore');
      await page.fill('textarea[placeholder*="Partner Expectations"]',
        'Looking for a well-educated, family-oriented partner with good values. ' +
        'Someone who is understanding, supportive, and has a positive outlook towards life.'
      );

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Horoscope', { state: 'visible' });
    });

    // Step 8: Horoscope
    await test.step('Fill in horoscope details', async () => {
      await page.selectOption('select:has-text("Time of Birth")', 'Morning');
      await page.fill('input[placeholder*="Birth Place"]', 'Mumbai, Maharashtra');
      await page.selectOption('select:has-text("Birth Star"]', 'Rohini');
      await page.selectOption('select:has-text("Zodiac Sign"]', 'Taurus');
      await page.selectOption('select:has-text("Manglik"]', 'No');
      await page.fill('textarea[placeholder*="Additional Horoscope Details"]',
        'Born in Rohini nakshatra, Taurus zodiac sign. No dosha present as per horoscope analysis.'
      );

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Photos', { state: 'visible' });
    });

    // Step 9: Photos
    await test.step('Upload photos', async () => {
      // Note: File upload testing might need special handling in Playwright
      // This is a basic structure - actual implementation may vary

      // Test photo upload interface
      await expect(page.locator('button:has-text("Upload Photos")')).toBeVisible();
      await expect(page.locator('text=Upload professional photos')).toBeVisible();

      // Simulate photo upload (this would need actual file upload setup)
      // await page.setInputFiles('input[type="file"]', 'test-photo.jpg');

      await page.click('button:has-text("Next")');
      await page.waitForSelector('text=Preview', { state: 'visible' });
    });

    // Step 10: Preview and Generate Biodata
    await test.step('Preview biodata and generate PDF', async () => {
      // Wait for preview to load
      await page.waitForSelector('[data-testid="biodata-preview"]', { state: 'visible' });

      // Verify all sections are present in preview
      await expect(page.locator('text=Priya Sharma')).toBeVisible();
      await expect(page.locator('text=Senior Business Analyst')).toBeVisible();
      await expect(page.locator('text=Bachelor of Engineering')).toBeVisible();
      await expect(page.locator('text=Vegetarian')).toBeVisible();

      // Test template switching
      await page.click('button:has-text("Change Template")');
      await page.click('text=Elegant Template');
      await page.waitForSelector('[data-testid="biodata-preview"]', { state: 'visible' });

      // Generate PDF
      await page.click('button:has-text("Generate PDF")');

      // Wait for PDF generation to complete
      await page.waitForSelector('text=Biodata PDF generated successfully', { state: 'visible', timeout: 30000 });

      // Download PDF
      await page.click('button:has-text("Download PDF")');

      // Verify download
      await expect(page.locator('text=Download started')).toBeVisible({ timeout: 10000 });
    });

    // Step 11: Save and Share
    await test.step('Save and share biodata', async () => {
      // Save biodata
      await page.click('button:has-text("Save Biodata")');
      await page.waitForSelector('text=Biodata saved successfully', { state: 'visible' });

      // Test sharing functionality
      await page.click('button:has-text("Share Biodata")');
      await page.waitForSelector('[data-testid="share-modal"]', { state: 'visible' });

      // Copy share link
      await page.click('button:has-text("Copy Link")');
      await expect(page.locator('text=Link copied to clipboard')).toBeVisible();

      // Test privacy settings
      await page.click('button:has-text("Privacy Settings")');
      await page.selectOption('select:has-text("Profile Visibility")', 'Public');
      await page.click('button:has-text("Save Settings")');

      await expect(page.locator('text=Privacy settings updated')).toBeVisible();
    });
  });

  test('marriage biodata form validation', async ({ page }) => {
    await test.step('Test form validation', async () => {
      // Try to submit empty personal info form
      await page.click('button:has-text("Next")');

      // Check for validation errors
      await expect(page.locator('text=Full name is required')).toBeVisible();
      await expect(page.locator('text=Gender is required')).toBeVisible();
      await expect(page.locator('text=Date of birth is required')).toBeVisible();

      // Test invalid email
      await page.fill('input[placeholder*="Email"]', 'invalid-email');
      await page.click('button:has-text("Next")');
      await expect(page.locator('text=Invalid email address')).toBeVisible();

      // Test valid email
      await page.fill('input[placeholder*="Email"]', 'valid@example.com');
      await page.click('button:has-text("Next")');
      await expect(page.locator('text=Invalid email address')).not.toBeVisible();

      // Test age validation
      await page.fill('input[placeholder*="Date of Birth"]', '2010-05-15'); // Too young
      await page.click('button:has-text("Next")');
      await expect(page.locator('text=Age must be 18 or above')).toBeVisible();
    });
  });

  test('photo upload and management', async ({ page }) => {
    await test.step('Test photo upload features', async () => {
      // Fill basic info to reach photo section
      await page.fill('input[placeholder*="Full Name"]', 'Photo Test User');
      await page.selectOption('select:has-text("Gender")', 'Female');
      await page.fill('input[placeholder*="Date of Birth"]', '1995-05-15');

      // Navigate through sections to reach photos
      await page.click('button:has-text("Next")'); // Contact
      await page.click('button:has-text("Next")'); // Family
      await page.click('button:has-text("Next")'); // Education
      await page.click('button:has-text("Next")'); // Occupation
      await page.click('button:has-text("Next")'); // Lifestyle
      await page.click('button:has-text("Next")'); // Partner
      await page.click('button:has-text("Next")'); // Horoscope

      await page.waitForSelector('text=Photos', { state: 'visible' });

      // Test photo upload interface
      await expect(page.locator('button:has-text("Upload Photos")')).toBeVisible();
      await expect(page.locator('text=Maximum 6 photos allowed')).toBeVisible();

      // Test photo requirements display
      await expect(page.locator('text=Photos should be clear and recent')).toBeVisible();
      await expect(page.locator('text=Inappropriate photos will be rejected')).toBeVisible();
    });
  });

  test('privacy and security features', async ({ page }) => {
    await test.step('Test privacy features', async () => {
      // Navigate to a section where privacy settings might be available
      await page.fill('input[placeholder*="Full Name"]', 'Privacy Test User');
      await page.selectOption('select:has-text("Gender")', 'Female');
      await page.fill('input[placeholder*="Date of Birth"]', '1995-05-15');

      // Look for privacy controls
      await expect(page.locator('button:has-text("Privacy Settings")')).toBeVisible();

      // Test privacy modal
      await page.click('button:has-text("Privacy Settings")');
      await page.waitForSelector('[data-testid="privacy-modal"]', { state: 'visible' });

      // Test different privacy options
      await expect(page.locator('select:has-text("Profile Visibility")')).toBeVisible();
      await expect(page.locator('select:has-text("Contact Information")')).toBeVisible();
      await expect(page.locator('select:has-text("Photos")')).toBeVisible();

      // Test privacy settings save
      await page.selectOption('select:has-text("Profile Visibility")', 'Private');
      await page.click('button:has-text("Save Settings")');
      await expect(page.locator('text=Privacy settings updated')).toBeVisible();
    });
  });

  test('mobile responsiveness for marriage biodata', async ({ page }) => {
    await test.step('Test mobile responsiveness', async () => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Test form layout on mobile
      await expect(page.locator('input[placeholder*="Full Name"]')).toBeVisible();
      await expect(page.locator('select:has-text("Gender")')).toBeVisible();
      await expect(page.locator('button:has-text("Next")')).toBeVisible();

      // Test form scrolling on mobile
      await page.fill('input[placeholder*="Full Name"]', 'Mobile User');
      await page.selectOption('select:has-text("Gender")', 'Female');
      await page.fill('input[placeholder*="Date of Birth"]', '1995-05-15');

      // Scroll down to find more fields
      await page.evaluate(() => window.scrollBy(0, 500));
      await expect(page.locator('input[placeholder*="Height"]')).toBeVisible();

      // Reset to desktop viewport
      await page.setViewportSize({ width: 1280, height: 720 });
    });
  });

  test('search and match features', async ({ page }) => {
    await test.step('Test search functionality', async () => {
      // Look for search features (might be in a different section)
      // This test assumes there's a search or browse profiles feature
      const searchExists = await page.locator('input[placeholder*="Search"]').count() > 0;

      if (searchExists) {
        await page.fill('input[placeholder*="Search"]', 'Software Engineer');
        await page.press('Enter');
        await page.waitForTimeout(2000); // Wait for search results

        // Test search filters
        await expect(page.locator('select:has-text("Age")')).toBeVisible();
        await expect(page.locator('select:has-text("Location")')).toBeVisible();
      }
    });
  });

  test('performance optimization for large forms', async ({ page }) => {
    await test.step('Test performance with large forms', async () => {
      // Measure time to fill the complete form
      const startTime = Date.now();

      // Fill all form sections quickly
      await page.fill('input[placeholder*="Full Name"]', 'Performance Test');
      await page.selectOption('select:has-text("Gender")', 'Female');
      await page.fill('input[placeholder*="Date of Birth"]', '1995-05-15');
      await page.fill('input[placeholder*="Email"]', 'test@example.com');
      await page.fill('input[placeholder*="Phone"]', '+91 98765 43210');

      const fillTime = Date.now() - startTime;
      console.log(`Form fill time: ${fillTime}ms`);
      expect(fillTime).toBeLessThan(2000); // Should fill within 2 seconds

      // Test form responsiveness with rapid inputs
      const rapidStartTime = Date.now();
      for (let i = 0; i < 10; i++) {
        await page.fill('input[placeholder*="Full Name"]', `Test ${i}`);
      }
      const rapidTime = Date.now() - rapidStartTime;
      console.log(`Rapid input time: ${rapidTime}ms`);
      expect(rapidTime).toBeLessThan(1000); // Should handle rapid inputs within 1 second
    });
  });
});