# Quick Start Guide - Supabase Setup

## 5-Minute Overview

This guide gets you started with Supabase setup in the shortest time possible. For detailed instructions, see [SUPABASE_CHECKLIST.md](./SUPABASE_CHECKLIST.md).

---

## What You'll Need

- [ ] Email address for Supabase account
- [ ] 15-20 minutes of time
- [ ] Internet connection

---

## Step 1: Create Supabase Project (5 min)

1. Go to [https://supabase.com](https://supabase.com) → Sign up
2. Click "New project"
3. Fill in:
   - **Name**: `hostel-meal-management`
   - **Password**: Generate and save it
   - **Region**: Closest to you (e.g., Mumbai for India)
   - **Plan**: Free
4. Wait 2-3 minutes for setup

---

## Step 2: Get Your Credentials (2 min)

1. In Supabase dashboard: Settings → API
2. Copy **Project URL** → Paste in `.env` file
3. Copy **anon public key** → Paste in `.env` file

Your `.env` should look like:
```env
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
```

4. Save `.env` and restart dev server

---

## Step 3: Run Migrations (3 min)

1. In Supabase: Click **SQL Editor**
2. Open `supabase/migrations/001_initial_schema.sql`
3. Copy all → Paste in SQL Editor → Click "Run"
4. Open `supabase/migrations/002_rls_policies.sql`
5. Copy all → Paste in SQL Editor → Click "Run"

---

## Step 4: Create Storage Buckets (5 min)

### Bucket 1: Profile Pictures
1. Supabase → Storage → "New bucket"
2. Name: `profile-pictures`, Public: **ON**, Size: 2MB
3. Go to SQL Editor, paste and run:

```sql
CREATE POLICY "Allow public read access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'profile-pictures');

CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'profile-pictures');

CREATE POLICY "Allow users to update own files"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'profile-pictures' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Allow users to delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'profile-pictures' AND auth.uid()::text = (storage.foldername(name))[1]);
```

### Bucket 2: Expense Receipts
1. Storage → "New bucket"
2. Name: `expense-receipts`, Public: **OFF**, Size: 5MB
3. Go to SQL Editor, paste and run:

```sql
CREATE POLICY "Allow managers to view receipts"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);

CREATE POLICY "Allow manager uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);

CREATE POLICY "Allow managers to update receipts"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);

CREATE POLICY "Allow managers to delete receipts"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND (SELECT role FROM users WHERE id = auth.uid()) = 'manager'
);
```

---

## Step 5: Test & Create Manager (3 min)

1. Start app: `npm run dev`
2. Register a new account in the app
3. In Supabase: Table Editor → users → Find your row
4. Change `role` from `student` to `manager` → Save
5. Log out and log back in → You should see manager features

**Alternative** (SQL Editor):
```sql
UPDATE users
SET role = 'manager'
WHERE email = 'your-email@example.com';
```

---

## Step 6: Load Test Data (Optional, 2 min)

1. **First**: Register 6 accounts through the app:
   - manager@hostel.com
   - john.doe@student.com
   - jane.smith@student.com
   - bob.wilson@student.com
   - alice.brown@student.com
   - charlie.davis@student.com

2. Open `TEST_DATA.sql`
3. Copy all → SQL Editor → Run
4. Update manager role (see Step 5)

---

## Verification Checklist

Setup is complete when:

- [ ] Can login to the application
- [ ] Manager account shows dashboard with stats
- [ ] Can plan meals as student
- [ ] Can add expenses as manager
- [ ] Profile picture upload works
- [ ] No errors in browser console

---

## Troubleshooting

### "Failed to connect"
- Check `.env` has correct URL and key
- Restart dev server after changing `.env`
- Verify Supabase project isn't paused

### "Permission denied"
- Re-run `002_rls_policies.sql` migration
- Log out and log back in
- Check user role in users table

### "Storage upload fails"
- Verify buckets exist in Storage tab
- Check policies are configured (run SQL above)
- For receipts: Ensure logged in as manager

---

## What's Next?

After setup is complete:

1. **Configure Settings**
   - Login as manager → Settings
   - Set meal deadlines and pricing

2. **Add Students**
   - Create student accounts
   - Record initial deposits

3. **Set Up Menus**
   - Add meal menus for upcoming days

4. **Test Everything**
   - Plan meals as student
   - Record expenses as manager
   - Verify calculations

---

## Documentation Files

- **SUPABASE_SETUP.md** - Detailed step-by-step guide with explanations
- **SUPABASE_CHECKLIST.md** - Complete checklist with ~50 steps
- **SUPABASE_SETUP_SUMMARY.md** - Schema overview and recommendations
- **TEST_DATA.sql** - Sample data for testing (6 users, meals, expenses)
- **This file** - 5-minute quick start

---

## Need Help?

1. Check browser console for errors (F12)
2. Check Supabase Logs tab for database errors
3. See SUPABASE_SETUP.md → Troubleshooting section
4. Common issues have solutions in SUPABASE_CHECKLIST.md

---

## Success!

If you completed all steps, you're ready to use the system. Start by:
- Logging in as manager
- Exploring the dashboard
- Creating meal menus
- Adding student accounts

**Estimated Total Time**: 15-20 minutes

---

**Remember**: Keep your database password and credentials secure!

**Last Updated**: 2025-10-14
