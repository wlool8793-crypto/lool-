# Complete Setup & Deployment Guide

## Your Supabase Project
**URL:** https://ovmdsyzdqmmfokejnyjx.supabase.co
**Dashboard:** https://supabase.com/dashboard/project/ovmdsyzdqmmfokejnyjx

---

## Step 1: Create Storage Buckets (5 minutes)

### A. Go to Storage Section
1. Open your Supabase dashboard: https://supabase.com/dashboard/project/ovmdsyzdqmmfokejnyjx/storage/buckets
2. Click **"Storage"** in the left sidebar

### B. Create "profile-pictures" Bucket
1. Click **"New bucket"** button (green button, top right)
2. Fill in the form:
   ```
   Name: profile-pictures
   Public bucket: ✅ TOGGLE ON (important!)
   File size limit: 2 MB
   Allowed MIME types: (leave empty for all images)
   ```
3. Click **"Create bucket"**

### C. Create "expense-receipts" Bucket
1. Click **"New bucket"** again
2. Fill in the form:
   ```
   Name: expense-receipts
   Public bucket: ❌ TOGGLE OFF (keep private)
   File size limit: 5 MB
   Allowed MIME types: (leave empty)
   ```
3. Click **"Create bucket"**

### D. Apply Storage Policies
1. Click **"SQL Editor"** in the left sidebar
2. Click **"New query"**
3. Open the file: `/workspaces/lool-/meal-management-system/setup-storage-buckets.sql`
4. Copy the ENTIRE contents
5. Paste into SQL Editor
6. Click **"Run"** (bottom right)
7. You should see: "Success. No rows returned"

---

## Step 2: Load Test Data (Optional - 2 minutes)

This creates sample accounts for easy testing:

1. Still in **SQL Editor**, click **"New query"**
2. Open: `/workspaces/lool-/meal-management-system/meal-management-system/TEST_DATA.sql`
3. Copy entire contents
4. Paste and click **"Run"**

**Test Accounts Created:**
```
Manager Account:
  Email: manager@hostel.com
  Password: Manager@123

Student Accounts:
  john.doe@student.com / Student@123
  jane.smith@student.com / Student@123
  bob.wilson@student.com / Student@123
  alice.brown@student.com / Student@123
  charlie.davis@student.com / Student@123
```

---

## Step 3: Test the Application Locally

Your dev server is already running at: http://localhost:3000

### Test Checklist:

#### Authentication Tests
- [ ] Register a new student account
- [ ] Register a new manager account (use a special signup link or set role in DB)
- [ ] Login with test accounts
- [ ] Logout
- [ ] Try invalid credentials

#### Student Features Tests
- [ ] View dashboard
- [ ] Plan meals for upcoming days
- [ ] Add guest meals
- [ ] View financial summary
- [ ] Check meal menu
- [ ] View notifications
- [ ] Update profile
- [ ] Upload profile picture

#### Manager Features Tests
- [ ] View manager dashboard
- [ ] Add new students
- [ ] Record deposits
- [ ] Add expenses with receipts
- [ ] View meal reports
- [ ] Generate financial reports
- [ ] Update meal menu
- [ ] Configure settings (deadlines, pricing)
- [ ] Send announcements

---

## Step 4: Deploy to Vercel (5 minutes)

### A. Install Vercel CLI
```bash
npm install -g vercel
```

### B. Login to Vercel
```bash
vercel login
```

### C. Deploy from Project Directory
```bash
cd /workspaces/lool-/meal-management-system
vercel --prod
```

### D. Add Environment Variables
After deployment, go to your Vercel dashboard:
1. Go to Project Settings → Environment Variables
2. Add these variables:
   ```
   VITE_SUPABASE_URL = https://ovmdsyzdqmmfokejnyjx.supabase.co
   VITE_SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92bWRzeXpkcW1tZm9rZWpueWp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0MjE4MjcsImV4cCI6MjA3NTk5NzgyN30.8PddAteVuyCVbEZBjhmFnM7YwVikVcN5t0oZ1sQ57_w
   ```
3. Redeploy: `vercel --prod`

---

## Step 5: Deploy to Netlify (Alternative - 5 minutes)

### A. Install Netlify CLI
```bash
npm install -g netlify-cli
```

### B. Login to Netlify
```bash
netlify login
```

### C. Deploy
```bash
cd /workspaces/lool-/meal-management-system
netlify deploy --prod
```

### D. Add Environment Variables
In Netlify dashboard:
1. Site Settings → Environment Variables
2. Add the same VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
3. Trigger new deploy

---

## Step 6: Post-Deployment Testing

Test the live application:
- [ ] Open deployed URL
- [ ] Test registration
- [ ] Test login
- [ ] Test all student features
- [ ] Test all manager features
- [ ] Test on mobile device
- [ ] Test offline mode (PWA)
- [ ] Test file uploads

---

## Troubleshooting

### Storage Buckets Not Working
- Verify buckets exist in Supabase Storage
- Check bucket names are exact: `profile-pictures` and `expense-receipts`
- Verify policies were applied (run verification query in SQL)
- Check bucket permissions (public vs private)

### Authentication Issues
- Verify environment variables are set correctly
- Check Supabase URL and anon key
- Ensure email confirmation is disabled (for testing)
- Check RLS policies are active

### Deployment Issues
- Run `npm run build` locally first to check for errors
- Verify environment variables in deployment platform
- Check build logs for specific errors
- Ensure Node version compatibility

---

## Next Steps After Setup

1. **Customize Branding**
   - Update logo and app name
   - Change color scheme in Tailwind config
   - Update favicon and PWA icons

2. **Configure Email**
   - Set up SMTP in Supabase
   - Enable email notifications
   - Customize email templates

3. **Set Up Monitoring**
   - Enable Supabase logs
   - Set up error tracking (Sentry)
   - Monitor performance

4. **Production Checklist**
   - Enable email confirmation
   - Set up backup strategy
   - Configure custom domain
   - Enable SSL/HTTPS
   - Set up analytics

---

## Support Files Location

- SQL Scripts: `/workspaces/lool-/meal-management-system/setup-storage-buckets.sql`
- Test Data: `/workspaces/lool-/meal-management-system/meal-management-system/TEST_DATA.sql`
- Migrations: `/workspaces/lool-/meal-management-system/meal-management-system/supabase/migrations/`
- Environment: `/workspaces/lool-/meal-management-system/.env`

---

## Quick Commands Reference

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Test Supabase connection
node test-connection.mjs

# Deploy to Vercel
vercel --prod

# Deploy to Netlify
netlify deploy --prod
```

---

**You're almost done! Just create those storage buckets and you're ready to go! 🚀**
