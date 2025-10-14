# Supabase Setup Checklist - Quick Start Guide

This is your quick-reference checklist for setting up Supabase for the Hostel Meal Management System. For detailed instructions, see [SUPABASE_SETUP.md](./SUPABASE_SETUP.md).

---

## Prerequisites

- [ ] Valid email address
- [ ] Internet connection
- [ ] Project files downloaded
- [ ] Basic understanding of the system

**Time Required**: 15-20 minutes

---

## Phase 1: Create Supabase Project

### 1.1 Sign Up & Create Project

- [ ] Go to [https://supabase.com](https://supabase.com)
- [ ] Sign up/Sign in (GitHub recommended)
- [ ] Click "New project"
- [ ] Fill in project details:
  - Name: `hostel-meal-management`
  - Database Password: Generate and **save securely**
  - Region: Select closest to your users (e.g., Mumbai for India)
  - Plan: Free
- [ ] Click "Create new project"
- [ ] Wait 2-3 minutes for provisioning

### 1.2 Get Your Credentials

- [ ] Go to Settings > API in Supabase dashboard
- [ ] Copy **Project URL** (looks like: `https://xxxxx.supabase.co`)
- [ ] Copy **anon public** key (starts with `eyJ...`)
- [ ] Update `.env` file in project root:
  ```env
  VITE_SUPABASE_URL=https://your-project-id.supabase.co
  VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- [ ] Save `.env` file
- [ ] Restart development server if running

---

## Phase 2: Run Database Migrations

### 2.1 Initial Schema Migration

- [ ] In Supabase dashboard, go to SQL Editor
- [ ] Open file: `supabase/migrations/001_initial_schema.sql`
- [ ] Copy entire contents
- [ ] Paste into SQL Editor
- [ ] Click "Run" button
- [ ] Verify success message appears

**What this creates**:
- 8 core tables (users, meals, deposits, expenses, meal_settings, menu, announcements, notifications)
- 4 views for reporting
- Indexes for performance
- Triggers for automatic timestamps
- Helper functions for calculations

### 2.2 Row Level Security Migration

- [ ] Open file: `supabase/migrations/002_rls_policies.sql`
- [ ] Copy entire contents
- [ ] Paste into SQL Editor (clear previous query first)
- [ ] Click "Run" button
- [ ] Verify success message appears

**What this creates**:
- RLS policies for all tables
- Helper functions for role checking
- Security enforcement at database level
- Audit logging capability (optional)

### 2.3 Verify Database Setup

- [ ] Go to Table Editor in Supabase dashboard
- [ ] Verify these tables exist:
  - [ ] users
  - [ ] meals
  - [ ] deposits
  - [ ] expenses
  - [ ] meal_settings
  - [ ] menu
  - [ ] announcements
  - [ ] notifications
- [ ] Click on `meal_settings` table
- [ ] Verify one row exists with default settings

---

## Phase 3: Set Up Storage Buckets

### 3.1 Create Profile Pictures Bucket

- [ ] Go to Storage in Supabase dashboard
- [ ] Click "New bucket"
- [ ] Configure:
  - Name: `profile-pictures`
  - Public: **ON**
  - File size limit: `2MB`
- [ ] Click "Create bucket"

### 3.2 Configure Profile Pictures Policies

- [ ] Click on `profile-pictures` bucket
- [ ] Go to Policies tab
- [ ] Create 4 policies (use SQL Editor):

**Policy 1: Public Read Access**
```sql
CREATE POLICY "Allow public read access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'profile-pictures');
```

**Policy 2: Authenticated Upload**
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'profile-pictures');
```

**Policy 3: Users Update Own Files**
```sql
CREATE POLICY "Allow users to update own files"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);
```

**Policy 4: Users Delete Own Files**
```sql
CREATE POLICY "Allow users to delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);
```

### 3.3 Create Expense Receipts Bucket

- [ ] Go back to Storage
- [ ] Click "New bucket"
- [ ] Configure:
  - Name: `expense-receipts`
  - Public: **OFF**
  - File size limit: `5MB`
- [ ] Click "Create bucket"

### 3.4 Configure Expense Receipts Policies

- [ ] Click on `expense-receipts` bucket
- [ ] Go to Policies tab
- [ ] Create 4 policies (use SQL Editor):

**Policy 1: Managers View Receipts**
```sql
CREATE POLICY "Allow managers to view receipts"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

**Policy 2: Managers Upload Receipts**
```sql
CREATE POLICY "Allow manager uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

**Policy 3: Managers Update Receipts**
```sql
CREATE POLICY "Allow managers to update receipts"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

**Policy 4: Managers Delete Receipts**
```sql
CREATE POLICY "Allow managers to delete receipts"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

### 3.5 Verify Storage Setup

- [ ] Go to Storage in Supabase dashboard
- [ ] Verify both buckets exist:
  - [ ] `profile-pictures` (Public)
  - [ ] `expense-receipts` (Private)
- [ ] Check each bucket has policies configured

---

## Phase 4: Configure Authentication

### 4.1 Email Authentication

- [ ] Go to Authentication > Settings
- [ ] Verify Email is enabled (should be by default)
- [ ] Configure email settings:
  - **Enable email confirmations**: OFF for development, ON for production
  - **Secure email change**: ON
  - **Double confirm email changes**: ON

### 4.2 Site URL and Redirect URLs

- [ ] In Authentication > Settings, scroll to Site URL
- [ ] Set Site URL:
  - Development: `http://localhost:3000`
  - Production: Your actual domain
- [ ] Scroll to Redirect URLs
- [ ] Add these URLs (comma-separated):
  ```
  http://localhost:3000/**,
  http://localhost:5173/**,
  https://yourdomain.com/**
  ```

### 4.3 Password Requirements

- [ ] In Authentication > Settings, scroll to Password section
- [ ] Configure (recommended):
  - Minimum length: `8` characters
  - Other requirements: Optional (app has its own validation)

### 4.4 Session Settings

- [ ] Scroll to Sessions section
- [ ] Configure:
  - JWT expiry: `3600` seconds (default)
  - Refresh token rotation: **ON**
  - Reuse interval: `10` seconds

### 4.5 Rate Limiting

- [ ] Scroll to Rate Limits section
- [ ] Configure:
  - Sign-in: `5` attempts/hour/IP
  - Sign-up: `10` attempts/hour/IP
  - Password reset: `5` attempts/hour/IP

### 4.6 Disable Unused Auth Providers

- [ ] Scroll to Auth Providers section
- [ ] Disable all except:
  - [ ] Email (keep enabled)
  - [ ] Google (disable unless needed)
  - [ ] GitHub (disable unless needed)
  - [ ] Facebook, Twitter, etc. (disable all)

---

## Phase 5: Verification & Testing

### 5.1 Verify Database Setup

- [ ] Go to Table Editor
- [ ] Check all 8 tables exist
- [ ] Open `meal_settings` table
- [ ] Verify default settings row exists
- [ ] Check RLS is enabled on all tables (indicator in top-right)

### 5.2 Verify Storage Setup

- [ ] Go to Storage
- [ ] Verify both buckets exist with correct visibility
- [ ] Check policies are configured for each bucket

### 5.3 Test Application Connection

- [ ] Ensure `.env` has correct credentials
- [ ] Start development server: `npm run dev`
- [ ] Open application in browser
- [ ] Try to register a new account
- [ ] Check Supabase Dashboard:
  - [ ] Go to Authentication > Users
  - [ ] Verify new user appears
  - [ ] Go to Table Editor > users
  - [ ] Verify user row exists with correct data

### 5.4 Create First Manager Account

**Option A: Manual Update in Supabase**
- [ ] Go to Table Editor > users
- [ ] Find your user row
- [ ] Click to edit
- [ ] Change `role` from `student` to `manager`
- [ ] Click Save
- [ ] Log out and log back in to the application

**Option B: Using SQL**
```sql
-- Replace 'your-email@example.com' with your actual email
UPDATE users
SET role = 'manager'
WHERE email = 'your-email@example.com';
```

### 5.5 Test Manager Access

- [ ] Log in with manager account
- [ ] Verify access to:
  - [ ] Dashboard with full statistics
  - [ ] User management
  - [ ] Expense management
  - [ ] Meal settings
  - [ ] All reports

### 5.6 Test Student Access (Optional)

- [ ] Register a new student account (different email)
- [ ] Log in as student
- [ ] Verify limited access:
  - [ ] Can view own meals
  - [ ] Can plan meals
  - [ ] Cannot access other students' data
  - [ ] Cannot access manager features

---

## Phase 6: Load Test Data (Optional)

If you want to test with sample data:

- [ ] Open file: `TEST_DATA.sql` (created alongside this checklist)
- [ ] Review the SQL commands
- [ ] Update email addresses in the file to real ones you can access
- [ ] Go to SQL Editor in Supabase
- [ ] Copy and paste the test data SQL
- [ ] Click "Run"
- [ ] Verify data appears in tables

**Note**: You'll need to manually update the first user's role to 'manager' after creating test accounts.

---

## Phase 7: Security Checklist

### 7.1 Environment Variables

- [ ] `.env` file is in `.gitignore`
- [ ] No credentials committed to version control
- [ ] Service role key NOT used in frontend
- [ ] Credentials stored securely

### 7.2 Database Security

- [ ] RLS enabled on all tables
- [ ] Policies tested and working
- [ ] No service_role key in frontend code
- [ ] Audit logging considered (optional)

### 7.3 Storage Security

- [ ] Profile pictures bucket is public (by design)
- [ ] Receipts bucket is private
- [ ] Storage policies enforce manager-only access for receipts
- [ ] File size limits configured

### 7.4 Authentication Security

- [ ] Rate limiting enabled
- [ ] Email confirmation configured (for production)
- [ ] Strong password requirements
- [ ] Redirect URLs configured correctly
- [ ] Unused auth providers disabled

### 7.5 Production Readiness (Before Going Live)

- [ ] Enable email confirmation
- [ ] Set up custom domain
- [ ] Configure SMTP for emails (optional)
- [ ] Test all features thoroughly
- [ ] Set up database backups
- [ ] Enable 2FA on Supabase account
- [ ] Review all security settings
- [ ] Configure monitoring/alerts
- [ ] Test with different user roles
- [ ] Enable HTTPS redirect

---

## Quick Commands Reference

### Check if connection works:
```bash
# Start dev server
npm run dev

# Open browser to http://localhost:3000
# Try registering an account
```

### Manually create manager account:
```sql
-- In Supabase SQL Editor
UPDATE users
SET role = 'manager'
WHERE email = 'your-email@example.com';
```

### Check RLS policies:
```sql
-- In Supabase SQL Editor
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### Reset database (WARNING: Deletes all data):
```sql
-- In Supabase SQL Editor
DROP VIEW IF EXISTS meal_counts_by_date CASCADE;
DROP VIEW IF EXISTS student_financial_summary CASCADE;
DROP VIEW IF EXISTS monthly_expense_summary CASCADE;
DROP VIEW IF EXISTS monthly_meal_statistics CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS announcements CASCADE;
DROP TABLE IF EXISTS menu CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS meals CASCADE;
DROP TABLE IF EXISTS deposits CASCADE;
DROP TABLE IF EXISTS meal_settings CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
DROP FUNCTION IF EXISTS calculate_user_monthly_meal_cost CASCADE;
DROP FUNCTION IF EXISTS is_manager CASCADE;
DROP FUNCTION IF EXISTS is_student CASCADE;
DROP FUNCTION IF EXISTS get_user_role CASCADE;
DROP FUNCTION IF EXISTS is_active_user CASCADE;
DROP FUNCTION IF EXISTS is_meal_deadline_passed CASCADE;
DROP FUNCTION IF EXISTS validate_meal_update CASCADE;
DROP FUNCTION IF EXISTS audit_trigger_function CASCADE;

-- Then re-run both migration files
```

---

## Common Issues & Quick Fixes

### Issue: "Failed to connect to Supabase"
**Fix**:
1. Check `.env` file exists and has correct values
2. Restart dev server after changing `.env`
3. Verify Supabase project is not paused

### Issue: "Permission denied" errors
**Fix**:
1. Verify RLS policies were applied (check Table Editor)
2. Re-run `002_rls_policies.sql` migration
3. Log out and log back in

### Issue: Storage upload fails
**Fix**:
1. Check bucket exists
2. Verify policies are configured
3. Check file size is within limits
4. For receipts: Ensure user is a manager

### Issue: Email confirmation not working
**Fix**:
1. Check spam folder
2. For dev: Disable email confirmation in Auth settings
3. Check email logs in Authentication > Logs

### Issue: Migration errors
**Fix**:
1. Some errors okay if re-running (tables already exist)
2. Use reset script above to start fresh if needed
3. Run migrations in order: 001 then 002

---

## Success Indicators

Your setup is complete when:

- [ ] All tables visible in Table Editor
- [ ] Both storage buckets exist with policies
- [ ] Can register and login to application
- [ ] Manager account created and functional
- [ ] Can plan meals as student
- [ ] Can record expenses as manager
- [ ] Profile picture upload works
- [ ] No console errors in browser
- [ ] RLS preventing unauthorized access

---

## Next Steps After Setup

1. **Configure Initial Settings**
   - Log in as manager
   - Go to Settings page
   - Configure meal deadlines and pricing

2. **Create Student Accounts**
   - Add student users through the application
   - Or manually in Supabase Table Editor

3. **Set Up Initial Data**
   - Create meal menus
   - Record initial deposits
   - Post welcome announcement

4. **Test Thoroughly**
   - Test as both student and manager
   - Verify calculations are correct
   - Test all features

5. **Production Deployment**
   - Create separate production Supabase project
   - Follow security checklist for production
   - Deploy application to hosting service

---

## Support Resources

- **Detailed Guide**: [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)
- **Test Data**: [TEST_DATA.sql](./TEST_DATA.sql)
- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Migration Files**: `supabase/migrations/` directory

---

## Checklist Summary

Total steps: ~50-60 checkboxes
Estimated time: 15-20 minutes
Difficulty: Beginner-friendly

**Remember**: Keep your database password and credentials secure!

---

**Last Updated**: January 2025
**Version**: 1.0
