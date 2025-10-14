# Supabase Setup Guide for Hostel Meal Management System

This comprehensive guide will walk you through setting up Supabase for the Hostel Meal Management System from scratch. Follow each step carefully to ensure proper configuration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Creating a Supabase Project](#creating-a-supabase-project)
3. [Getting Your Credentials](#getting-your-credentials)
4. [Running Database Migrations](#running-database-migrations)
5. [Setting Up Storage Buckets](#setting-up-storage-buckets)
6. [Configuring Authentication](#configuring-authentication)
7. [Verifying Your Setup](#verifying-your-setup)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## Prerequisites

Before starting, make sure you have:

- A valid email address
- Internet connection
- Access to the project's `.env` file
- Basic understanding of databases (helpful but not required)

**Estimated Time**: 15-20 minutes

---

## Creating a Supabase Project

### Step 1: Sign Up for Supabase

1. Go to [https://supabase.com](https://supabase.com)
2. Click on **"Start your project"** or **"Sign in"** in the top-right corner
3. Sign up using one of these methods:
   - GitHub account (recommended)
   - Email and password
   - GitLab account
   - Bitbucket account

4. If using email/password:
   - Enter your email address
   - Create a strong password
   - Verify your email through the confirmation link sent to your inbox

### Step 2: Create a New Project

1. After signing in, you'll see the Supabase dashboard
2. Click on **"New project"** button
3. Fill in the project details:

   **Organization**:
   - Select an existing organization or create a new one
   - Organization name: `My Organization` (or your preferred name)

   **Project Details**:
   - **Name**: `hostel-meal-management` (or your preferred name)
   - **Database Password**: Generate a strong password
     - Click the **"Generate a password"** button
     - **IMPORTANT**: Copy and save this password securely
     - You'll need it for direct database access (optional)
   - **Region**: Select the region closest to your users
     - For India: `Mumbai (ap-south-1)`
     - For US: `East US (us-east-1)`
     - For Europe: `Frankfurt (eu-central-1)`
   - **Pricing Plan**: Select **"Free"** (perfect for development and small deployments)

4. Click **"Create new project"**
5. Wait 2-3 minutes while Supabase provisions your database and infrastructure
6. You'll see a progress indicator - don't close the browser tab

---

## Getting Your Credentials

### Step 1: Access Your Project Settings

1. Once your project is ready, you'll be on the project dashboard
2. In the left sidebar, click on **"Settings"** (gear icon at the bottom)
3. In the settings menu, click on **"API"**

### Step 2: Copy Your Credentials

You'll see several important pieces of information:

#### Project URL
- Located in the **"Project URL"** section
- Looks like: `https://xxxxxxxxxxxxx.supabase.co`
- Copy this entire URL

#### API Keys
- Located in the **"Project API keys"** section
- You'll see two keys:
  - **anon/public**: This is what you need (safe to use in your frontend)
  - **service_role**: DO NOT use this in your frontend (server-only)

- Copy the **anon public** key (the long string starting with `eyJ...`)

### Step 3: Update Your .env File

1. Open the `.env` file in your project root directory
2. Replace the placeholder values:

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example**:
```env
VITE_SUPABASE_URL=https://xyzabcdefgh.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5emFiY2RlZmdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE2MjYyNzI0MDAsImV4cCI6MTk0MTg0ODQwMH0.zT9NxZmVkYmU5YzljZGQwYmYxZjVkYjQ2ZGRkYjQ2ZGRkYjQ2ZGRkYjQ2ZGRkYjQ2
```

3. Save the file
4. **Restart your development server** if it's running

**Important Notes**:
- Never commit the `.env` file to version control
- Keep your credentials secure
- The anon key is safe for frontend use (it's public)
- Never expose your service_role key in frontend code

---

## Running Database Migrations

Database migrations create all the necessary tables, views, and security policies for your application.

### Step 1: Access the SQL Editor

1. In your Supabase dashboard, find the left sidebar
2. Click on **"SQL Editor"** (icon looks like `</>`)
3. You'll see the SQL editor interface

### Step 2: Run the Initial Schema Migration

1. In your project, locate the file:
   ```
   supabase/migrations/001_initial_schema.sql
   ```

2. Open this file and copy its entire contents

3. Back in the Supabase SQL Editor:
   - Paste the copied SQL code into the editor
   - Click **"Run"** button (bottom-right corner)
   - Wait for the query to complete (should take 2-5 seconds)

4. You should see a success message: **"Success. No rows returned"**

**What this migration creates**:
- `users` table - Stores student and manager profiles
- `meals` table - Daily meal planning records
- `deposits` table - Student payment records
- `expenses` table - Hostel expense records
- `meal_settings` table - Configuration for deadlines and pricing
- `menu` table - Daily meal menus
- `announcements` table - System announcements
- `notifications` table - User notifications
- Helper views for reporting
- Automatic timestamp triggers

### Step 3: Run the RLS Policies Migration

1. Locate the file:
   ```
   supabase/migrations/002_rls_policies.sql
   ```

2. Copy its entire contents

3. In the Supabase SQL Editor:
   - Clear the previous query
   - Paste the new SQL code
   - Click **"Run"** button
   - Wait for completion

4. You should see a success message again

**What this migration creates**:
- Row Level Security (RLS) policies for all tables
- Ensures students can only access their own data
- Allows managers to access all data
- Protects sensitive information

### Step 4: Verify Tables Were Created

1. In the left sidebar, click on **"Table Editor"**
2. You should see all these tables:
   - `users`
   - `meals`
   - `deposits`
   - `expenses`
   - `meal_settings`
   - `menu`
   - `announcements`
   - `notifications`

3. Click on any table to see its structure
4. All tables should be empty initially (except `meal_settings` which has one default row)

**Troubleshooting Migration Issues**:
- If you get an error, read the error message carefully
- Common issue: Running migrations twice - some errors are okay if tables already exist
- You can drop all tables and re-run if needed (see Troubleshooting section)

---

## Setting Up Storage Buckets

Storage buckets are used to store files like profile pictures and expense receipts.

### Step 1: Access Storage

1. In the left sidebar, click on **"Storage"** (folder icon)
2. You'll see the storage interface
3. Click on **"New bucket"** button

### Step 2: Create Profile Pictures Bucket

1. Click **"New bucket"** button
2. Fill in the details:
   - **Name**: `profile-pictures`
   - **Public bucket**: Toggle **ON** (enable this)
     - This allows profile pictures to be viewed without authentication
   - **File size limit**: `2MB` (recommended)
   - **Allowed MIME types**: Leave empty or add:
     - `image/jpeg`
     - `image/png`
     - `image/jpg`
     - `image/webp`

3. Click **"Create bucket"**

### Step 3: Configure Profile Pictures Bucket Policies

1. Click on the `profile-pictures` bucket you just created
2. Click on **"Policies"** tab at the top
3. Click **"New policy"** button
4. Select **"Custom"** policy type
5. Use this configuration:

**Policy 1: Allow authenticated users to upload**
```sql
-- Policy name: Allow authenticated uploads
-- Allowed operations: INSERT

CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'profile-pictures');
```

**Policy 2: Allow users to update their own files**
```sql
-- Policy name: Allow users to update own files
-- Allowed operations: UPDATE

CREATE POLICY "Allow users to update own files"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'profile-pictures' AND auth.uid()::text = (storage.foldername(name))[1]);
```

**Policy 3: Allow users to delete their own files**
```sql
-- Policy name: Allow users to delete own files
-- Allowed operations: DELETE

CREATE POLICY "Allow users to delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'profile-pictures' AND auth.uid()::text = (storage.foldername(name))[1]);
```

**Policy 4: Allow public read access**
```sql
-- Policy name: Allow public read access
-- Allowed operations: SELECT

CREATE POLICY "Allow public read access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'profile-pictures');
```

### Step 4: Create Expense Receipts Bucket

1. Click **"Back"** or click on **"Storage"** in the sidebar
2. Click **"New bucket"** button
3. Fill in the details:
   - **Name**: `expense-receipts`
   - **Public bucket**: Toggle **OFF** (keep this private)
     - Only authenticated managers should access receipts
   - **File size limit**: `5MB`
   - **Allowed MIME types**:
     - `image/jpeg`
     - `image/png`
     - `image/jpg`
     - `application/pdf`

4. Click **"Create bucket"**

### Step 5: Configure Expense Receipts Bucket Policies

1. Click on the `expense-receipts` bucket
2. Click on **"Policies"** tab
3. Add these policies:

**Policy 1: Allow managers to upload receipts**
```sql
-- Policy name: Allow manager uploads
-- Allowed operations: INSERT

CREATE POLICY "Allow manager uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

**Policy 2: Allow managers to view all receipts**
```sql
-- Policy name: Allow managers to view receipts
-- Allowed operations: SELECT

CREATE POLICY "Allow managers to view receipts"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

**Policy 3: Allow managers to update receipts**
```sql
-- Policy name: Allow managers to update receipts
-- Allowed operations: UPDATE

CREATE POLICY "Allow managers to update receipts"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

**Policy 4: Allow managers to delete receipts**
```sql
-- Policy name: Allow managers to delete receipts
-- Allowed operations: DELETE

CREATE POLICY "Allow managers to delete receipts"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

### Step 6: Verify Storage Setup

1. Go back to **"Storage"** in the sidebar
2. You should see both buckets:
   - `profile-pictures` (Public)
   - `expense-receipts` (Private)
3. Each should have policies configured

---

## Configuring Authentication

### Step 1: Access Authentication Settings

1. In the left sidebar, click on **"Authentication"** (person icon)
2. Click on **"Settings"** (not the sidebar Settings, but the tab at the top)
3. You'll see various authentication configuration options

### Step 2: Configure Email Authentication

1. Scroll to **"Auth Providers"** section
2. **Email** should already be enabled by default
3. Configure email settings:

**Email Templates** (optional but recommended):
1. Click on **"Email Templates"** in the left sub-menu
2. Customize these templates if desired:
   - **Confirm signup** - Sent when new users register
   - **Invite user** - Sent when managers invite students
   - **Magic Link** - For passwordless login (optional)
   - **Change Email Address** - Email change confirmation
   - **Reset Password** - Password reset emails

**Recommended Email Confirmation Settings**:
1. Go back to **"Settings"** under Authentication
2. Under **"Email"** provider settings:
   - **Enable email confirmations**: Toggle **OFF** for development (easier testing)
     - Toggle **ON** for production (more secure)
   - **Secure email change**: Toggle **ON** (recommended)
   - **Double confirm email changes**: Toggle **ON** (recommended)

### Step 3: Configure Site URL and Redirect URLs

1. Still in Authentication > Settings
2. Scroll to **"Site URL"** section:
   - **Site URL**: Enter your application URL
     - Development: `http://localhost:3000`
     - Production: `https://yourdomain.com`

3. Scroll to **"Redirect URLs"** section:
   - Add allowed redirect URLs (comma-separated):
   ```
   http://localhost:3000/**,
   http://localhost:5173/**,
   https://yourdomain.com/**
   ```
   - The `**` wildcard allows any path under the domain

### Step 4: Configure Password Requirements

1. In Authentication > Settings
2. Scroll to **"Password"** section
3. Recommended settings:
   - **Minimum password length**: `8` characters
   - **Require uppercase letters**: Optional (your preference)
   - **Require lowercase letters**: Optional (your preference)
   - **Require numbers**: Optional (your preference)
   - **Require special characters**: Optional (your preference)

**Note**: The application has its own password validation, so Supabase defaults are fine.

### Step 5: Configure Session Settings

1. Scroll to **"Sessions"** section
2. Recommended settings:
   - **JWT expiry**: `3600` seconds (1 hour) - default is fine
   - **Refresh token rotation**: Toggle **ON** (recommended for security)
   - **Reuse interval**: `10` seconds (prevents token reuse)

### Step 6: Disable Unused Auth Providers (Security Best Practice)

1. Scroll back to **"Auth Providers"** section
2. Disable any providers you're not using:
   - Google (unless you want social login)
   - GitHub (unless you want social login)
   - Facebook, Twitter, etc.

**Only keep enabled**:
- Email (required for this application)

### Step 7: Configure Rate Limiting (Important for Security)

1. Scroll to **"Rate Limits"** section
2. These protect against brute force attacks
3. Recommended settings (defaults are usually good):
   - **Sign-in rate limit**: `5` attempts per hour per IP
   - **Sign-up rate limit**: `10` attempts per hour per IP
   - **Password reset rate limit**: `5` attempts per hour per IP

---

## Verifying Your Setup

### Step 1: Check Database Tables

1. Go to **"Table Editor"** in the sidebar
2. Verify all tables exist:
   - [ ] `users`
   - [ ] `meals`
   - [ ] `deposits`
   - [ ] `expenses`
   - [ ] `meal_settings`
   - [ ] `menu`
   - [ ] `announcements`
   - [ ] `notifications`

3. Click on `meal_settings` table
4. You should see one row with default settings for the current month

### Step 2: Check Storage Buckets

1. Go to **"Storage"** in the sidebar
2. Verify buckets exist:
   - [ ] `profile-pictures` (Public)
   - [ ] `expense-receipts` (Private)

3. Click on each bucket
4. Verify policies are configured (check the "Policies" tab)

### Step 3: Test Your Connection

1. Make sure your `.env` file has the correct credentials
2. Start your development server:
   ```bash
   npm run dev
   ```

3. Open your browser to `http://localhost:3000` (or the port shown)
4. Try to register a new account
5. Check Supabase dashboard:
   - Go to **"Authentication"** > **"Users"**
   - You should see your new user listed

6. After registering, check **"Table Editor"** > **"users"**
   - You should see a new row with your user data

### Step 4: Verify Row Level Security

1. Try logging in as a student
2. Students should NOT be able to:
   - View other students' meals
   - View other students' financial data
   - Access manager-only features

3. Create a manager account (you'll need to manually update the role):
   - Go to **"Table Editor"** > **"users"**
   - Find your user row
   - Change `role` from `student` to `manager`
   - Click **"Save"**

4. Log in as manager and verify you can access all features

---

## Security Considerations

### 1. Environment Variables

**DO NOT**:
- Commit `.env` file to version control
- Share your credentials publicly
- Use service_role key in frontend code
- Hard-code credentials in your application

**DO**:
- Add `.env` to `.gitignore`
- Use environment variables for all secrets
- Rotate keys if they're exposed
- Use different projects for development and production

### 2. Row Level Security (RLS)

**Why RLS is Important**:
- Provides database-level access control
- Prevents unauthorized data access
- Works even if client-side security is bypassed
- Protects against SQL injection

**Verify RLS is Enabled**:
1. Go to **"Table Editor"**
2. Click on any table
3. Check the top-right corner - should say **"RLS enabled"**
4. If it says **"RLS disabled"**, click to enable it

**Testing RLS**:
- Try accessing another user's data via API
- Should get empty results or permission denied error
- RLS policies automatically filter data based on auth.uid()

### 3. Storage Security

**Profile Pictures (Public Bucket)**:
- Anyone can view pictures (by design)
- Only authenticated users can upload
- Users can only modify their own files
- Public access needed for displaying avatars

**Expense Receipts (Private Bucket)**:
- Only managers can access
- Students cannot view or upload receipts
- Protects sensitive financial documents
- Manager role checked in policies

### 4. Authentication Security

**Best Practices**:
- Enforce strong passwords in production
- Enable email confirmation for production
- Use HTTPS in production (required)
- Implement rate limiting
- Monitor authentication logs
- Set up 2FA for Supabase dashboard access

**Monitoring**:
1. Go to **"Authentication"** > **"Users"**
2. Monitor new registrations
3. Check for suspicious activity
4. Review failed login attempts

### 5. API Security

**The anon/public key**:
- Safe to use in frontend
- Row Level Security protects data
- Users can only access allowed data
- Rate limiting prevents abuse

**The service_role key**:
- Never use in frontend
- Bypasses RLS (full admin access)
- Only use in secure backend/server functions
- Treat like a database password

### 6. Database Backups

**Automatic Backups** (Free tier):
- Daily backups for 7 days
- Check: **"Settings"** > **"Database"** > **"Backups"**

**Manual Backups**:
1. Go to **"Settings"** > **"Database"**
2. Scroll to **"Database Backups"**
3. Click **"Create backup"** for manual backup

**Point-in-Time Recovery** (Paid plans):
- Upgrade plan for point-in-time recovery
- Recommended for production

### 7. Production Checklist

Before deploying to production:

- [ ] Enable email confirmation
- [ ] Set up custom domain
- [ ] Configure SMTP for emails (optional)
- [ ] Enable RLS on all tables
- [ ] Test all storage policies
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Enable 2FA on Supabase account
- [ ] Use strong database password
- [ ] Set up monitoring/alerts
- [ ] Review all security policies
- [ ] Test with different user roles
- [ ] Enable HTTPS redirect
- [ ] Configure CORS properly

---

## Troubleshooting

### Issue 1: "Failed to connect to Supabase"

**Symptoms**:
- Application shows connection error
- Cannot register or login
- Network errors in console

**Solutions**:
1. Verify `.env` file exists in root directory
2. Check credentials are correct (no extra spaces)
3. Ensure variables start with `VITE_`
4. Restart development server after changing `.env`
5. Check Supabase project is not paused (free tier pauses after inactivity)
6. Verify internet connection
7. Check browser console for specific errors

### Issue 2: "Permission denied" or "No rows returned"

**Symptoms**:
- Can register but cannot access data
- Tables appear empty
- API calls fail with permission errors

**Solutions**:
1. Verify RLS policies were applied:
   - Go to **"Authentication"** > **"Policies"**
   - Each table should have policies listed
2. Re-run the `002_rls_policies.sql` migration
3. Check user is authenticated (try logging out and back in)
4. Verify `auth.uid()` matches user ID in database
5. Check user role is set correctly in users table

### Issue 3: Storage Upload Fails

**Symptoms**:
- Profile picture upload fails
- Receipt upload fails
- "Policy violation" errors

**Solutions**:
1. Verify storage buckets exist
2. Check bucket policies are configured
3. Verify file size is within limits
4. Check file type is allowed
5. For profile pictures: Ensure user is authenticated
6. For receipts: Ensure user has manager role
7. Check browser console for specific error

### Issue 4: Email Confirmation Not Working

**Symptoms**:
- Not receiving confirmation emails
- Cannot complete registration

**Solutions**:
1. Check spam/junk folder
2. Verify email provider isn't blocking Supabase emails
3. For development: Disable email confirmation:
   - **"Authentication"** > **"Settings"** > **"Email"**
   - Toggle off **"Enable email confirmations"**
4. Check Supabase email logs:
   - **"Authentication"** > **"Logs"**
5. Consider setting up custom SMTP (paid feature)

### Issue 5: Migration Errors

**Symptoms**:
- SQL errors when running migrations
- Tables not created
- "Relation already exists" errors

**Solutions**:

**If tables already exist**:
- Some errors are okay if re-running migrations
- Tables won't be recreated if they exist
- Check Table Editor to verify tables exist

**To start fresh** (WARNING: Deletes all data):
```sql
-- Run this in SQL Editor to drop all tables
DROP VIEW IF EXISTS meal_counts_by_date CASCADE;
DROP VIEW IF EXISTS student_financial_summary CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS announcements CASCADE;
DROP TABLE IF EXISTS menu CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS meals CASCADE;
DROP TABLE IF EXISTS deposits CASCADE;
DROP TABLE IF EXISTS meal_settings CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
```

Then re-run both migrations.

### Issue 6: Authentication Redirect Issues

**Symptoms**:
- After login, redirected to wrong page
- "Invalid redirect URL" error
- Stuck in redirect loop

**Solutions**:
1. Check redirect URLs in Authentication settings
2. Verify Site URL matches your domain
3. Add all development URLs:
   ```
   http://localhost:3000/**
   http://localhost:5173/**
   http://127.0.0.1:3000/**
   ```
4. Use `**` wildcard for all paths
5. Clear browser cookies and cache

### Issue 7: "Project is Paused"

**Symptoms**:
- Cannot access database
- Supabase dashboard shows "Project Paused"
- Connection timeouts

**Solutions**:
1. Free tier projects pause after 7 days of inactivity
2. Click **"Restore project"** in dashboard
3. Takes 1-2 minutes to restore
4. Consider upgrading to Pro plan for production
5. Make a request to your project weekly to prevent auto-pause

### Issue 8: Slow Query Performance

**Symptoms**:
- Queries take a long time
- Application feels sluggish
- Timeout errors

**Solutions**:
1. Indexes are already configured in migrations
2. For large datasets, implement pagination
3. Use Supabase query filters effectively
4. Check query performance in Supabase dashboard:
   - **"Database"** > **"Query Performance"**
5. Consider enabling read replicas (paid feature)

---

## Next Steps

### 1. Create Your First Manager Account

1. Register a new account through your application
2. Go to Supabase dashboard
3. **"Table Editor"** > **"users"**
4. Find your user and change `role` to `manager`
5. Log out and log back in

### 2. Configure Meal Settings

1. Log in as manager
2. Go to Settings page
3. Configure:
   - Meal deadlines
   - Fixed meal costs (if any)
   - Guest meal pricing
   - Late cancellation penalties

### 3. Set Up Initial Data

As a manager:
1. Add student accounts
2. Record initial deposits
3. Create meal menus for upcoming days
4. Post an announcement welcoming students

### 4. Test the System

1. Create test student accounts
2. Plan meals as a student
3. Add guest meals
4. Record expenses as manager
5. Verify financial calculations
6. Test notifications
7. Try the reports section

### 5. Production Deployment

Once everything works locally:
1. Create a new Supabase project for production
2. Follow this guide again for production project
3. Deploy your application to a hosting service:
   - Vercel (recommended)
   - Netlify
   - Railway
   - Your own server

4. Update production environment variables
5. Test thoroughly before going live

### 6. Optional Enhancements

**Custom Email Templates**:
- Customize email templates in Supabase
- Add your hostel's branding
- Personalize messages

**Database Backup Strategy**:
- Set up automated backups
- Export data regularly
- Document recovery procedures

**Monitoring and Logs**:
- Set up error tracking (Sentry, etc.)
- Monitor Supabase logs regularly
- Set up alerts for errors

**Performance Monitoring**:
- Monitor query performance
- Optimize slow queries
- Implement caching if needed

---

## Additional Resources

### Supabase Documentation
- [Supabase Docs](https://supabase.com/docs)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage Guide](https://supabase.com/docs/guides/storage)
- [Authentication Guide](https://supabase.com/docs/guides/auth)

### Video Tutorials
- [Supabase Crash Course](https://www.youtube.com/watch?v=zBZgdTb-dns)
- [Row Level Security Explained](https://www.youtube.com/watch?v=Ow_Uzedfohk)

### Community Support
- [Supabase Discord](https://discord.supabase.com)
- [Supabase GitHub Discussions](https://github.com/supabase/supabase/discussions)

### Project Documentation
- [Main README](./README.md)
- [User Guide](./USER_GUIDE.md) (if available)
- [Deployment Guide](./DEPLOYMENT.md) (if available)

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the Browser Console**:
   - Open Developer Tools (F12)
   - Look for error messages
   - Check Network tab for failed requests

2. **Check Supabase Logs**:
   - **"Logs"** in Supabase dashboard
   - Review recent errors and queries

3. **Review This Guide**:
   - Re-read relevant sections
   - Follow troubleshooting steps

4. **Search Documentation**:
   - Supabase documentation
   - Project README
   - GitHub issues

5. **Ask for Help**:
   - Create a GitHub issue
   - Post in Supabase Discord
   - Contact your system administrator

---

## Summary Checklist

Use this checklist to verify your setup is complete:

### Account Setup
- [ ] Created Supabase account
- [ ] Created new project
- [ ] Saved database password securely

### Credentials
- [ ] Copied Project URL
- [ ] Copied Anon Key
- [ ] Updated `.env` file
- [ ] Restarted development server

### Database
- [ ] Ran `001_initial_schema.sql` migration
- [ ] Ran `002_rls_policies.sql` migration
- [ ] Verified all tables exist
- [ ] Checked RLS is enabled

### Storage
- [ ] Created `profile-pictures` bucket (public)
- [ ] Created `expense-receipts` bucket (private)
- [ ] Configured policies for both buckets
- [ ] Verified buckets are accessible

### Authentication
- [ ] Configured email authentication
- [ ] Set Site URL
- [ ] Added Redirect URLs
- [ ] Configured rate limiting
- [ ] Disabled unused auth providers

### Testing
- [ ] Started development server
- [ ] Registered test account
- [ ] Verified user appears in database
- [ ] Tested basic functionality
- [ ] Created manager account

### Security
- [ ] `.env` file not committed to git
- [ ] RLS enabled on all tables
- [ ] Storage policies configured
- [ ] Rate limiting enabled
- [ ] Email confirmation configured (for production)

---

**Congratulations!** If you've completed all steps, your Supabase backend is fully configured and ready to use. You can now focus on building your application features.

**Remember**: This guide is for the Hostel Meal Management System. Keep it handy for reference and share it with your team members.

---

**Last Updated**: January 2025
**Guide Version**: 1.0
**Supabase Version**: Latest (as of January 2025)
