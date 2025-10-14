# 🚀 Deployment Guide - Hostel Meal Management System

Complete guide for deploying your application to production.

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Completed build successfully (`npm run build` works)
- ✅ Supabase project configured
- ✅ Environment variables ready
- ✅ Git repository (for some platforms)

---

## Option 1: Deploy to Vercel (Recommended)

**Why Vercel?**
- ✅ Automatic deployments from Git
- ✅ Free tier available
- ✅ Built-in CI/CD
- ✅ Global CDN
- ✅ Automatic HTTPS

### Step 1: Prepare Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create GitHub repository and push
git remote add origin <your-repo-url>
git push -u origin main
```

### Step 2: Deploy to Vercel

**Via Vercel Dashboard:**

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `meal-management-system`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

5. Add Environment Variables:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

6. Click "Deploy"

**Via Vercel CLI:**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd meal-management-system
vercel

# Follow prompts and add environment variables when asked
```

### Step 3: Configure Custom Domain (Optional)

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

---

## Option 2: Deploy to Netlify

### Via Netlify Dashboard

1. Go to https://netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect your Git repository
4. Configure:
   - **Base directory:** `meal-management-system`
   - **Build command:** `npm run build`
   - **Publish directory:** `meal-management-system/dist`

5. Add Environment Variables:
   - Go to Site Settings → Build & Deploy → Environment
   - Add:
     ```
     VITE_SUPABASE_URL=your_supabase_url
     VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

6. Click "Deploy site"

### Via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize
cd meal-management-system
netlify init

# Deploy
netlify deploy --prod
```

---

## Option 3: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in the Variables tab
6. Railway will auto-detect Vite and deploy

---

## Option 4: Deploy to Render

1. Go to https://render.com
2. Click "New +" → "Static Site"
3. Connect your repository
4. Configure:
   - **Build Command:** `cd meal-management-system && npm install && npm run build`
   - **Publish Directory:** `meal-management-system/dist`
5. Add environment variables
6. Click "Create Static Site"

---

## Option 5: Self-Hosted (VPS/Server)

### Requirements
- Ubuntu 20.04+ or similar
- Node.js 18+
- Nginx or Apache
- SSL certificate (Let's Encrypt)

### Step 1: Build Locally

```bash
cd meal-management-system
npm install
npm run build
```

### Step 2: Upload to Server

```bash
# Using SCP
scp -r dist/* user@your-server:/var/www/hostel-meal-system/

# Or using rsync
rsync -avz dist/ user@your-server:/var/www/hostel-meal-system/
```

### Step 3: Configure Nginx

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/hostel-meal-system;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
}
```

### Step 4: SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Environment Variables

### Required Variables

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

### How to Set in Different Platforms

**Vercel:**
- Dashboard: Project Settings → Environment Variables
- CLI: `vercel env add VITE_SUPABASE_URL`

**Netlify:**
- Dashboard: Site Settings → Build & Deploy → Environment
- CLI: `netlify env:set VITE_SUPABASE_URL value`

**Railway:**
- Dashboard: Project → Variables tab

**Render:**
- Dashboard: Environment → Environment Variables

---

## Post-Deployment Checklist

### 1. Verify Deployment

- [ ] Site loads correctly
- [ ] All assets load (CSS, JS, images)
- [ ] No console errors
- [ ] Routes work (test navigation)

### 2. Test Authentication

- [ ] Can register new user
- [ ] Can login
- [ ] Can logout
- [ ] Password reset works (if enabled)

### 3. Test Features

- [ ] Student dashboard loads
- [ ] Manager dashboard loads (if manager)
- [ ] Meal planning works
- [ ] Deposits page works
- [ ] File uploads work
- [ ] Reports generate correctly

### 4. Performance Check

- [ ] Lighthouse score > 90
- [ ] Page load time < 3 seconds
- [ ] Images optimized
- [ ] Gzip enabled

### 5. Security Check

- [ ] HTTPS enabled
- [ ] Environment variables not exposed
- [ ] Supabase RLS working
- [ ] CORS configured correctly

---

## Troubleshooting

### Issue: "Failed to load environment variables"

**Solution:**
1. Verify variables start with `VITE_`
2. Rebuild after adding variables
3. Check for typos in variable names

### Issue: "Routes return 404"

**Solution:**
Add redirect rules:

**Vercel:** Already configured in `vercel.json`
**Netlify:** Already configured in `netlify.toml`
**Self-hosted:** Configure server rewrites

### Issue: "Blank page after deployment"

**Solution:**
1. Check browser console for errors
2. Verify base path in `vite.config.ts`
3. Check if assets are loading (Network tab)
4. Ensure build completed successfully

### Issue: "Supabase connection fails"

**Solution:**
1. Verify environment variables are set
2. Check Supabase project is not paused
3. Verify API URL and key are correct
4. Check CORS settings in Supabase

---

## CI/CD Setup

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: |
        cd meal-management-system
        npm ci

    - name: Build
      env:
        VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
        VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
      run: |
        cd meal-management-system
        npm run build

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        working-directory: ./meal-management-system
```

---

## Monitoring & Analytics

### 1. Vercel Analytics

```bash
npm install @vercel/analytics
```

Add to `src/main.tsx`:
```typescript
import { inject } from '@vercel/analytics';
inject();
```

### 2. Google Analytics

Add to `index.html`:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 3. Error Tracking (Sentry)

```bash
npm install @sentry/react
```

Configure in `src/main.tsx`:
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  integrations: [new Sentry.BrowserTracing()],
  tracesSampleRate: 1.0,
});
```

---

## Performance Optimization

### 1. Enable Compression

All platforms (Vercel, Netlify) automatically enable compression.

For self-hosted, ensure gzip is enabled in Nginx/Apache.

### 2. CDN Configuration

Vercel and Netlify provide global CDN automatically.

For self-hosted, consider:
- Cloudflare (free tier available)
- AWS CloudFront
- Google Cloud CDN

### 3. Cache Headers

Already configured in `vercel.json` and `netlify.toml`:
- Static assets: 1 year cache
- HTML: No cache (always fresh)

---

## Backup Strategy

### 1. Database Backups

Supabase automatically backs up your database.

**Manual backup:**
1. Go to Supabase Dashboard → Database
2. Click "Backups"
3. Create manual backup

### 2. Code Backups

- Push to GitHub regularly
- Use Git tags for releases
- Consider multiple remotes

### 3. Environment Variables

Store securely:
- Use password manager
- Keep separate production/staging configs
- Document in team wiki (without actual values)

---

## Scaling Considerations

### When to Scale

Monitor these metrics:
- Concurrent users > 100
- Response time > 1 second
- Database queries > 1000/hour

### How to Scale

**Supabase:**
- Upgrade to Pro plan
- Enable read replicas
- Use connection pooling

**Frontend:**
- Already on CDN (Vercel/Netlify)
- Implement code splitting
- Add service worker caching

**Server (if self-hosted):**
- Use load balancer
- Add more instances
- Enable caching layer (Redis)

---

## Support & Maintenance

### Regular Tasks

**Weekly:**
- Check error logs
- Monitor performance
- Review user feedback

**Monthly:**
- Update dependencies
- Review and update documentation
- Backup environment configs

**Quarterly:**
- Security audit
- Performance audit
- User acceptance testing

### Getting Help

- Check documentation
- Review troubleshooting section
- Check Supabase status page
- Contact platform support

---

## Quick Deploy Commands

### Vercel
```bash
vercel --prod
```

### Netlify
```bash
netlify deploy --prod
```

### Railway
```bash
railway up
```

---

**🎉 You're Ready to Deploy!**

Choose your platform, follow the steps, and your Hostel Meal Management System will be live!

**Recommended Flow:**
1. Start with Vercel (easiest)
2. Test thoroughly
3. Add custom domain
4. Set up monitoring
5. Celebrate! 🎊
