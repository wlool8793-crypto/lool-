# Cloud Provider Setup Progress

## 🎯 Goal
Set up 4 cloud providers to deploy 40+ proxy servers for free

---

## ☁️ Provider Setup Checklist

### 1. DigitalOcean - $200 Free Credit (60 days)
- [ ] Sign up at https://www.digitalocean.com/
- [ ] Verify email
- [ ] Add payment method
- [ ] Claim $200 credit
- [ ] Generate API token
- [ ] Add token to .env

**Steps:**
1. Go to: https://www.digitalocean.com/
2. Click "Sign Up"
3. Use email or GitHub
4. Verify your email
5. Add payment method (credit/debit card - won't be charged)
6. Get API token:
   - Go to: https://cloud.digitalocean.com/account/api/tokens
   - Click "Generate New Token"
   - Name: "IndianKanoon Scraper"
   - Check "Write" permissions
   - Copy the token (SAVE IT - only shown once!)

**Add to .env:**
```env
DIGITALOCEAN_TOKEN=dop_v1_YOUR_TOKEN_HERE
DIGITALOCEAN_VM_COUNT=15
```

---

### 2. Vultr - $100 Free Credit (30 days)
- [ ] Sign up at https://www.vultr.com/
- [ ] Verify email
- [ ] Add payment method
- [ ] Claim $100 credit
- [ ] Get API key
- [ ] Add key to .env

**Steps:**
1. Go to: https://www.vultr.com/
2. Click "Sign Up"
3. Verify email
4. Add payment method
5. Claim $100 credit (check promotions page)
6. Get API key:
   - Go to: https://my.vultr.com/settings/#settingsapi
   - Click "Enable API"
   - Copy API key

**Add to .env:**
```env
VULTR_API_KEY=YOUR_API_KEY_HERE
VULTR_VM_COUNT=10
```

---

### 3. Linode - $100 Free Credit (60 days)
- [ ] Sign up at https://www.linode.com/
- [ ] Verify email
- [ ] Add payment method
- [ ] Claim $100 credit
- [ ] Generate token
- [ ] Add token to .env

**Steps:**
1. Go to: https://www.linode.com/
2. Click "Sign Up"
3. Verify email
4. Add payment method
5. Get Personal Access Token:
   - Go to: https://cloud.linode.com/profile/tokens
   - Click "Create a Personal Access Token"
   - Label: "IndianKanoon Scraper"
   - Expiry: Never
   - Permissions: Select all
   - Copy token

**Add to .env:**
```env
LINODE_TOKEN=YOUR_TOKEN_HERE
LINODE_VM_COUNT=10
```

---

### 4. Oracle Cloud - Always Free Tier (OPTIONAL)
- [ ] Sign up at https://www.oracle.com/cloud/free/
- [ ] Verify email and phone
- [ ] Add payment method (not charged for free tier)
- [ ] Generate API key
- [ ] Download private key
- [ ] Add credentials to .env

**Note:** Oracle setup is more complex. Start with the other 3 first!

---

## 📝 Current Status

**Completed:**
- ✅ SSH keys generated
- ✅ Dependencies installed
- ✅ Scripts ready

**Next Steps:**
1. Sign up for DigitalOcean (start here - easiest!)
2. Get API token
3. Add token to .env file
4. Test deployment
5. Repeat for other providers

---

## 💰 Total Free Credits Available

| Provider | Credit | Duration | Status |
|----------|--------|----------|--------|
| DigitalOcean | $200 | 60 days | ⬜ Not set up |
| Vultr | $100 | 30 days | ⬜ Not set up |
| Linode | $100 | 60 days | ⬜ Not set up |
| Oracle | Free Forever | Forever | ⬜ Optional |
| **Total** | **$400+** | - | - |

---

## 🎯 Recommended Order

1. **Start with DigitalOcean** (easiest, most generous)
2. **Add Vultr** (quick setup)
3. **Add Linode** (similar to DO)
4. **Skip Oracle** (complex, can add later)

With just DigitalOcean + Vultr, you'll get:
- 25 proxy servers
- $300 in credits
- Enough to complete the project!

---

## 🔧 After Getting Tokens

Once you have at least one API token:

```bash
# 1. Update .env file
nano .env

# 2. Test deployment
python deploy_vms.py

# 3. Monitor
python dashboard.py
```

---

## ⚠️ Important Notes

1. **Don't skip email verification** - required for credits
2. **Save API tokens immediately** - shown only once
3. **Set billing alerts** - prevent unexpected charges
4. **Start with 1 provider** - test before scaling
5. **Remember to cleanup** - run cleanup_vms.py when done

---

## 📞 Need Help?

- DigitalOcean Support: https://www.digitalocean.com/support
- Vultr Support: https://my.vultr.com/support/
- Linode Support: https://www.linode.com/support/

---

**Ready to start? Go to: https://www.digitalocean.com/**
