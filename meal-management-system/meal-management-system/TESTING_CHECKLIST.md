# ✅ Testing Checklist - Hostel Meal Management System

Comprehensive testing guide to ensure all features work correctly after Supabase setup.

---

## Pre-Testing Setup

### 1. Verify Environment
- [ ] Supabase credentials added to `.env`
- [ ] Dev server running (`npm run dev`)
- [ ] Browser console open (F12)
- [ ] No console errors on page load

### 2. Verify Database
- [ ] Migrations run successfully
- [ ] All 8 tables exist
- [ ] RLS policies enabled
- [ ] Storage buckets created

---

## 🔐 Authentication Testing

### Registration
- [ ] Can access `/register` page
- [ ] Form validation works (required fields)
- [ ] Password strength validation works
- [ ] Email format validation works
- [ ] Can register new student account
- [ ] Success toast appears
- [ ] Redirected to student dashboard
- [ ] User appears in Supabase auth table
- [ ] User record created in `users` table

### Login
- [ ] Can access `/login` page
- [ ] Form validation works
- [ ] Can login with correct credentials
- [ ] Error shown for wrong password
- [ ] Error shown for non-existent email
- [ ] Success toast appears
- [ ] Redirected to appropriate dashboard (role-based)
- [ ] Session persists on page refresh

### Logout
- [ ] Logout button visible when logged in
- [ ] Can click logout
- [ ] Session cleared
- [ ] Redirected to login page
- [ ] Cannot access protected routes after logout

### Password Reset (if enabled)
- [ ] "Forgot Password" link works
- [ ] Can enter email
- [ ] Reset email sent (check Supabase logs)
- [ ] Can reset password via email link

---

## 👨‍🎓 Student Features Testing

### Dashboard
- [ ] Loads without errors
- [ ] Shows correct user name
- [ ] Displays financial summary cards
- [ ] Shows upcoming meal deadlines
- [ ] Displays notifications (if any)
- [ ] Quick actions work (navigate to other pages)
- [ ] Charts render correctly (if using Recharts)

### Meal Planning (`/student/meals`)
- [ ] Calendar view loads
- [ ] Can select future dates
- [ ] Cannot select past dates
- [ ] Can toggle breakfast on/off
- [ ] Can toggle lunch on/off
- [ ] Can toggle dinner on/off
- [ ] Can add guest meals (number input)
- [ ] Save button works
- [ ] Success toast appears
- [ ] Changes persist after page refresh
- [ ] Meals locked after deadline (if configured)
- [ ] Locked meals show warning
- [ ] Can view meal history (past dates)

### Financial Summary (`/student/deposits`)
- [ ] Page loads correctly
- [ ] Shows total deposits
- [ ] Shows total expenses (meal costs)
- [ ] Shows current balance
- [ ] Deposit history table displays
- [ ] Can filter by date range
- [ ] CSV export works
- [ ] Transaction details correct
- [ ] Calculations are accurate

### Profile (`/student/profile`)
- [ ] Profile info displays correctly
- [ ] Can edit full name
- [ ] Can edit room number
- [ ] Can edit phone number
- [ ] Profile picture upload works
- [ ] Uploaded image displays
- [ ] Can change password
- [ ] Old password validation works
- [ ] New password validation works
- [ ] Password change success message
- [ ] Changes persist after refresh

---

## 👨‍💼 Manager Features Testing

### Access Control
- [ ] Create manager account (update role in Supabase)
- [ ] Login as manager
- [ ] Cannot access student routes
- [ ] Redirected to manager dashboard

### Manager Dashboard (`/manager/dashboard`)
- [ ] Loads without errors
- [ ] Shows total students count
- [ ] Shows total deposits
- [ ] Shows total expenses
- [ ] Shows meal statistics
- [ ] Charts render correctly
- [ ] All cards display proper data
- [ ] Quick actions work

### Student Management (`/manager/users`)
- [ ] Student list loads
- [ ] Shows all students
- [ ] Search functionality works
- [ ] Can filter by status (active/inactive)
- [ ] Can view student details
- [ ] Can edit student info
- [ ] Can activate/deactivate student
- [ ] Can add new student
- [ ] Email uniqueness validated
- [ ] Changes save correctly

### Meal Management (`/manager/meals`)
- [ ] Page loads correctly
- [ ] Can select date
- [ ] Shows meal counts (breakfast, lunch, dinner)
- [ ] Shows guest meal counts
- [ ] Student list with meal selections displays
- [ ] Can view individual student details
- [ ] CSV export works
- [ ] Can filter by meal type
- [ ] Totals calculate correctly

### Deposits Management (`/manager/deposits`)
- [ ] Deposits list loads
- [ ] Can add new deposit
- [ ] Can select student from dropdown
- [ ] Can enter amount
- [ ] Can select payment method
- [ ] Can add notes
- [ ] Deposit saves correctly
- [ ] Appears in list immediately
- [ ] Can filter by student
- [ ] Can filter by date range
- [ ] Can filter by payment method
- [ ] CSV export works
- [ ] Statistics update correctly

### Expenses Management (`/manager/expenses`)
- [ ] Expenses list loads
- [ ] Can add new expense
- [ ] Can select category (vegetables, rice, etc.)
- [ ] Can enter amount and description
- [ ] Can select date
- [ ] Receipt upload works
- [ ] Receipt displays in list
- [ ] Can click to view receipt
- [ ] Can delete expense
- [ ] Delete confirmation works
- [ ] Can filter by date range
- [ ] Can filter by category
- [ ] Category breakdown shows
- [ ] CSV export works
- [ ] Totals calculate correctly

### Menu Management (`/manager/menu`)
- [ ] Page loads correctly
- [ ] Date selector works
- [ ] Can view menu for selected date
- [ ] Can create new menu
- [ ] Can enter breakfast items
- [ ] Can enter lunch items
- [ ] Can enter dinner items
- [ ] Save button works
- [ ] Success message appears
- [ ] Menu persists after refresh
- [ ] Can edit existing menu
- [ ] Can delete menu
- [ ] Upcoming menus list displays
- [ ] Can navigate between dates

### Settings (`/manager/settings`)
- [ ] Settings page loads
- [ ] Current settings display
- [ ] Can change breakfast deadline time
- [ ] Can change lunch deadline time
- [ ] Can change dinner deadline time
- [ ] Can set fixed meal cost
- [ ] Can set guest meal price
- [ ] Can set late cancellation penalty
- [ ] Save button works
- [ ] Success message appears
- [ ] Settings persist after refresh
- [ ] Can reset to defaults
- [ ] Copy settings to next month works

---

## 📊 Reports Testing

### Financial Reports
- [ ] Can generate PDF report
- [ ] PDF downloads correctly
- [ ] PDF contains all data
- [ ] PDF formatted properly
- [ ] Can export to Excel
- [ ] Excel file downloads
- [ ] Excel contains multiple sheets
- [ ] Data is accurate

### Meal Reports
- [ ] Can generate meal statistics PDF
- [ ] Student breakdown included
- [ ] Guest meal counts shown
- [ ] Can export to Excel
- [ ] Charts/graphs display (if any)

### Student Reports
- [ ] Can select student
- [ ] Can select date range
- [ ] Can generate individual report
- [ ] Report shows deposits
- [ ] Report shows meals
- [ ] Report shows balance
- [ ] Can export to PDF
- [ ] Can export to Excel

---

## 📁 File Upload Testing

### Profile Pictures
- [ ] Can upload JPG image
- [ ] Can upload PNG image
- [ ] File size validation works (2MB limit)
- [ ] Image displays after upload
- [ ] Image persists after refresh
- [ ] Can replace existing image
- [ ] Old image removed from storage

### Expense Receipts (Manager)
- [ ] Can upload image receipt
- [ ] Can upload PDF receipt
- [ ] File size validation works (5MB limit)
- [ ] Receipt link appears in expense list
- [ ] Can view uploaded receipt
- [ ] Receipt opens in new tab
- [ ] Receipt viewable only by managers
- [ ] Students cannot access receipts

---

## 🔔 Notifications Testing

### Real-time Updates
- [ ] Notifications appear in real-time
- [ ] Badge count updates
- [ ] Can click to view notifications
- [ ] Can mark as read
- [ ] Read status persists
- [ ] Can delete notification
- [ ] Notification types work:
  - [ ] Meal deadline reminders
  - [ ] Deposit confirmations
  - [ ] Expense additions
  - [ ] Announcements

---

## 🌐 PWA Testing

### Offline Functionality
- [ ] Can install as PWA (desktop)
- [ ] Can install as PWA (mobile)
- [ ] Service worker registers
- [ ] Works offline (cached pages)
- [ ] Offline indicator shows
- [ ] Background sync queues updates
- [ ] Updates sync when back online

### Updates
- [ ] Update notification appears (if new version)
- [ ] Can update service worker
- [ ] Page reloads with new version

---

## 🎨 UI/UX Testing

### Responsive Design
- [ ] Works on mobile (< 640px)
- [ ] Works on tablet (640-1024px)
- [ ] Works on desktop (> 1024px)
- [ ] Navigation menu responsive
- [ ] Tables responsive (horizontal scroll if needed)
- [ ] Forms adapt to screen size
- [ ] Images scale correctly

### Dark Mode (if implemented)
- [ ] Can toggle dark mode
- [ ] All pages support dark mode
- [ ] Contrast is readable
- [ ] Images/icons visible
- [ ] Preference persists

### Navigation
- [ ] All nav links work
- [ ] Back button works
- [ ] Breadcrumbs work (if any)
- [ ] Can navigate using keyboard
- [ ] Focus indicators visible

### Forms
- [ ] Tab order logical
- [ ] Enter key submits forms
- [ ] Escape key closes modals
- [ ] Error messages clear
- [ ] Success feedback visible
- [ ] Loading states shown

---

## 🔒 Security Testing

### Access Control
- [ ] Students cannot access manager routes
- [ ] Managers cannot access student-specific data
- [ ] Cannot access other user's profile
- [ ] Cannot edit other user's meals
- [ ] Cannot view other user's financial data

### Data Protection
- [ ] Passwords not visible in network requests
- [ ] Tokens stored securely
- [ ] No sensitive data in localStorage
- [ ] RLS prevents unauthorized queries
- [ ] File uploads have proper permissions

### Input Validation
- [ ] SQL injection attempts fail
- [ ] XSS attempts sanitized
- [ ] File upload type validation
- [ ] File size limits enforced
- [ ] Email format validated
- [ ] Phone number format validated
- [ ] Amount fields accept only numbers

---

## ⚡ Performance Testing

### Load Times
- [ ] Initial page load < 3 seconds
- [ ] Route navigation < 1 second
- [ ] API requests < 500ms
- [ ] Images load quickly
- [ ] No layout shift (CLS)

### Data Loading
- [ ] Large lists paginated or virtualized
- [ ] Loading indicators shown
- [ ] Error states handled
- [ ] Empty states displayed
- [ ] Skeleton screens (if any)

### Browser Compatibility
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge
- [ ] Works on iOS
- [ ] Works on Android

---

## 🐛 Error Handling Testing

### Network Errors
- [ ] Graceful handling of offline state
- [ ] Retry mechanism works
- [ ] Error messages user-friendly
- [ ] Can recover from errors

### API Errors
- [ ] 401 errors redirect to login
- [ ] 403 errors show permission denied
- [ ] 404 errors handled
- [ ] 500 errors show friendly message
- [ ] Error boundaries catch React errors

### Edge Cases
- [ ] Empty data states handled
- [ ] Very long names/text handled
- [ ] Special characters in input
- [ ] Concurrent edits handled
- [ ] Expired sessions handled

---

## 📝 Data Integrity Testing

### Calculations
- [ ] Balance = Deposits - Meal Costs
- [ ] Meal costs calculated correctly
- [ ] Guest meal pricing correct
- [ ] Penalty calculations accurate
- [ ] Date range totals match

### Data Consistency
- [ ] Deposits sum matches total
- [ ] Meal counts match records
- [ ] User count accurate
- [ ] No orphaned records
- [ ] Foreign keys maintained

---

## 🎯 Final Checklist

### Pre-Launch
- [ ] All above tests passed
- [ ] No console errors
- [ ] No console warnings (critical)
- [ ] Lighthouse score > 90
- [ ] Accessibility check passed
- [ ] Tested with real data
- [ ] Backup taken

### Post-Launch Monitoring
- [ ] Set up error tracking
- [ ] Monitor performance
- [ ] Check user feedback
- [ ] Review logs regularly
- [ ] Test new features thoroughly

---

## 📋 Testing Tools

### Recommended Tools
```bash
# Lighthouse (Performance, Accessibility, SEO)
npm install -g lighthouse
lighthouse http://localhost:3000

# Accessibility
npm install -g @axe-core/cli
axe http://localhost:3000

# Bundle Analysis
npm run build -- --analyze
```

### Browser DevTools
- **Console:** Check for errors
- **Network:** Monitor API calls
- **Application:** Check localStorage, service worker
- **Lighthouse:** Run audits
- **Responsive:** Test different screen sizes

---

## 🎊 Testing Summary

**Total Tests:** 200+ checkpoints

**Categories:**
- Authentication: 15 tests
- Student Features: 40 tests
- Manager Features: 80 tests
- Reports: 15 tests
- File Uploads: 10 tests
- Notifications: 10 tests
- PWA: 8 tests
- UI/UX: 20 tests
- Security: 15 tests
- Performance: 10 tests
- Error Handling: 10 tests
- Data Integrity: 10 tests

---

**🎉 When All Tests Pass:**
Your Hostel Meal Management System is production-ready! 🚀

**Recommended Testing Order:**
1. Authentication (critical)
2. Student features (core functionality)
3. Manager features (admin operations)
4. Reports & exports
5. Edge cases & error handling
6. Performance & security
7. Cross-browser & responsive

**Good luck testing!** 🍀
