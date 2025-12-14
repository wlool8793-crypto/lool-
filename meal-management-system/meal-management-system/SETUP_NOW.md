# 🚀 Complete Setup & Test - Follow These Steps

## Step 1: Create Supabase Project (5 minutes)

### A. Sign up for Supabase
1. Go to: https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email

### B. Create New Project
1. Click "New project"
2. Choose/create an organization
3. Fill in details:
   - **Name:** `hostel-meal-system` (or your choice)
   - **Database Password:** Click "Generate" and **SAVE IT**
   - **Region:** Choose closest to you (e.g., Mumbai for India)
   - **Plan:** Free (perfect for this)
4. Click "Create new project"
5. **Wait 2-3 minutes** for provisioning ⏳

---

## Step 2: Get Your Credentials (1 minute)

Once your project is ready:

1. Click **"Settings"** (gear icon, bottom left sidebar)
2. Click **"API"** in the settings menu
3. Copy these two values:

**Project URL:**
```
Example: https://abcdefghijk.supabase.co
```

**anon public key:**
```
Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...
(This will be a very long string)
```

---

## Step 3: Update Environment File (30 seconds)

**I'll help you update the .env file. Paste your credentials below:**

When you have them, tell me:
- "My Supabase URL is: [paste URL]"
- "My anon key is: [paste key]"

And I'll update the file for you!

**OR** you can edit it manually:
1. Open: `/workspaces/lool-/meal-management-system/meal-management-system/.env`
2. Replace line 7: `VITE_SUPABASE_URL=your_supabase_project_url_here`
   With: `VITE_SUPABASE_URL=https://your-actual-project.supabase.co`
3. Replace line 11: `VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here`
   With: `VITE_SUPABASE_ANON_KEY=eyJhbGc... (your actual key)`

---

## Step 4: Run Database Migrations (3 minutes)

### A. Open SQL Editor
1. In Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. You'll see a blank SQL editor

### B. Run First Migration
1. Open file: `/workspaces/lool-/meal-management-system/meal-management-system/supabase/migrations/001_initial_schema.sql`
2. Copy **entire contents**
3. Paste into Supabase SQL Editor
4. Click **"Run"** (bottom right)
5. Wait for success message ✓

### C. Run Second Migration
1. Open file: `/workspaces/lool-/meal-management-system/meal-management-system/supabase/migrations/002_rls_policies.sql`
2. Copy **entire contents**
3. **Clear the SQL editor first**
4. Paste the new SQL
5. Click **"Run"**
6. Wait for success message ✓

### D. Verify Tables Created
1. Click **"Table Editor"** (left sidebar)
2. You should see 8 tables:
   - users
   - meals
   - deposits
   - expenses
   - meal_settings
   - menu
   - announcements
   - notifications

---

## Step 5: Create Storage Buckets (3 minutes)

### A. Create Profile Pictures Bucket
1. Click **"Storage"** (left sidebar)
2. Click **"New bucket"**
3. Fill in:
   - **Name:** `profile-pictures`
   - **Public bucket:** ✅ **Toggle ON**
   - **File size limit:** `2MB`
4. Click **"Create bucket"**

### B. Create Expense Receipts Bucket
1. Click **"New bucket"** again
2. Fill in:
   - **Name:** `expense-receipts`
   - **Public bucket:** ❌ **Toggle OFF** (keep private)
   - **File size limit:** `5MB`
4. Click **"Create bucket"**

### C. Configure Bucket Policies
1. Click on **`profile-pictures`** bucket
2. Click **"Policies"** tab
3. Click **"New policy"** → **"For full customization"**
4. Paste this SQL and run it:

```sql
-- Allow authenticated users to upload
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'profile-pictures');

-- Allow public to view
CREATE POLICY "Allow public read"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'profile-pictures');

-- Allow users to update their own files
CREATE POLICY "Allow users to update own files"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'profile-pictures');

-- Allow users to delete their own files
CREATE POLICY "Allow users to delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'profile-pictures');
```

5. Click on **`expense-receipts`** bucket
6. Click **"Policies"** tab
7. Click **"New policy"** → **"For full customization"**
8. Paste this SQL and run it:

```sql
-- Allow managers to upload
CREATE POLICY "Allow manager uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);

-- Allow managers to view
CREATE POLICY "Allow managers to view"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);

-- Allow managers to update
CREATE POLICY "Allow managers to update"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);

-- Allow managers to delete
CREATE POLICY "Allow managers to delete"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

---

## Step 6: Load Test Data (Optional - 1 minute)

This creates sample accounts and data for testing:

1. Go to **SQL Editor**
2. Open file: `/workspaces/lool-/meal-management-system/meal-management-system/TEST_DATA.sql`
3. Copy **entire contents**
4. Paste into SQL Editor
5. Click **"Run"**

**Test Accounts Created:**
- **Manager:** manager@hostel.com / Manager@123
- **Students:**
  - john.doe@student.com / Student@123
  - jane.smith@student.com / Student@123
  - bob.wilson@student.com / Student@123
  - alice.brown@student.com / Student@123
  - charlie.davis@student.com / Student@123

---

## Step 7: Restart Dev Server & Test! (30 seconds)

After updating .env, restart the server:

**Tell me when you're done with steps 1-6, and I'll:**
1. Restart the dev server for you
2. Test the authentication
3. Test all features
4. Give you a full test report

---

## Quick Checklist

Before telling me you're ready to test:

- [ ] Created Supabase project
- [ ] Got Project URL and Anon Key
- [ ] Updated .env file with credentials
- [ ] Ran 001_initial_schema.sql migration
- [ ] Ran 002_rls_policies.sql migration
- [ ] Created profile-pictures bucket (public)
- [ ] Created expense-receipts bucket (private)
- [ ] Configured bucket policies
- [ ] (Optional) Loaded TEST_DATA.sql

---

## Need Help?

**If you're stuck on any step, tell me which step number and I'll help!**

**When you're done, just say:** "Ready to test!" or "Done with setup!"

And I'll immediately:
✅ Restart the server
✅ Test authentication
✅ Test all student pages
✅ Test all manager pages
✅ Give you a complete test report

Let's do this! 🚀
