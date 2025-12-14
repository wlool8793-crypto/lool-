# Supabase Setup Summary & Schema Overview

## Overview

This document provides a comprehensive summary of the Hostel Meal Management System's database schema, security model, and setup requirements.

---

## Database Schema Summary

### Core Tables (8 Total)

#### 1. **users** - User Profiles
- **Purpose**: Stores student and manager profiles
- **Key Fields**:
  - `id` (UUID, references auth.users)
  - `email` (TEXT, unique)
  - `role` (TEXT: 'manager' or 'student')
  - `full_name`, `room_number`, `phone`
  - `profile_picture_url`
  - `is_active` (BOOLEAN)
- **Indexes**: 3 indexes (role, email, is_active)
- **Security**: RLS enabled, students see own profile + other students, managers see all

#### 2. **meals** - Daily Meal Planning
- **Purpose**: Tracks meal plans for each student by date
- **Key Fields**:
  - `user_id`, `meal_date`
  - `breakfast`, `lunch`, `dinner` (BOOLEAN)
  - `breakfast_locked`, `lunch_locked`, `dinner_locked` (deadline enforcement)
  - `guest_breakfast`, `guest_lunch`, `guest_dinner` (INTEGER, 0-10)
- **Indexes**: 4 indexes (user_id, meal_date, composite, upcoming meals)
- **Unique Constraint**: (user_id, meal_date)
- **Security**: Students manage own meals, managers see all

#### 3. **deposits** - Student Payments
- **Purpose**: Tracks student deposits and payments
- **Key Fields**:
  - `user_id`, `amount` (DECIMAL)
  - `deposit_date`, `month` (YYYY-MM format)
  - `payment_method` (cash/online/upi)
  - `recorded_by` (manager who recorded)
- **Indexes**: 4 indexes (user_id, month, date, recorded_by)
- **Security**: Students see own deposits, managers see all

#### 4. **expenses** - Hostel Expenses
- **Purpose**: Tracks all hostel expenses with receipts (transparency)
- **Key Fields**:
  - `amount`, `expense_date`, `month`
  - `category` (vegetables/rice/meat/spices/gas/utilities/other)
  - `description`, `receipt_url`
  - `recorded_by` (manager)
- **Indexes**: 4 indexes (month, date, category, recorded_by)
- **Security**: ALL authenticated users can view (transparency), only managers can modify

#### 5. **meal_settings** - Configuration
- **Purpose**: Monthly settings for deadlines and pricing
- **Key Fields**:
  - `month` (YYYY-MM, unique)
  - `breakfast_deadline_hour`, `lunch_deadline_hour`, `dinner_deadline_hour`
  - `dinner_deadline_previous_day` (BOOLEAN)
  - `fixed_meal_cost`, `late_cancellation_penalty`, `guest_meal_price`
- **Indexes**: 1 index (month)
- **Security**: All users can view, only managers can modify

#### 6. **menu** - Daily Menus
- **Purpose**: Daily meal menus for breakfast, lunch, dinner
- **Key Fields**:
  - `menu_date` (DATE, unique)
  - `breakfast_items`, `lunch_items`, `dinner_items` (TEXT)
  - `created_by` (manager)
- **Indexes**: 3 indexes (date, upcoming, created_by)
- **Security**: All users can view, only managers can modify

#### 7. **announcements** - System Announcements
- **Purpose**: Manager announcements to all students
- **Key Fields**:
  - `title`, `message`
  - `priority` (low/medium/high)
  - `created_by`, `expires_at`
- **Indexes**: 4 indexes (expires_at, created_at, priority, active)
- **Security**: All users can view active announcements, managers see all

#### 8. **notifications** - User Notifications
- **Purpose**: Personalized notifications and reminders
- **Key Fields**:
  - `user_id` (NULL for broadcast)
  - `title`, `message`
  - `type` (reminder/warning/info/alert)
  - `is_read` (BOOLEAN)
- **Indexes**: 4 indexes (user_id, is_read, created_at, type)
- **Security**: Users see own + broadcast notifications, managers see all

### Additional Tables

#### 9. **audit_log** (Optional)
- **Purpose**: Security audit trail for sensitive operations
- **Key Fields**: table_name, operation, user_id, old_data, new_data
- **Security**: Only managers can view

---

## Database Views (4 Total)

### 1. **meal_counts_by_date**
- Aggregates meal counts per date for kitchen planning
- Shows student count, breakfast/lunch/dinner counts
- Includes guest meal counts
- Useful for: Daily meal preparation planning

### 2. **student_financial_summary**
- Financial overview for each active student
- Shows total deposits, meal counts, guest meals
- Includes last deposit date and last meal date
- Useful for: Financial tracking and reporting

### 3. **monthly_expense_summary**
- Expenses grouped by month and category
- Shows count, total, average, min, max amounts
- Useful for: Budget analysis and expense tracking

### 4. **monthly_meal_statistics**
- Overall meal statistics by month
- Shows unique students, total meals by type
- Calculates average meals per student per day
- Useful for: Trend analysis and capacity planning

---

## Database Functions (9 Total)

### Security & Access Control Functions

1. **is_manager()** - Check if current user is a manager
2. **is_student()** - Check if current user is a student
3. **get_user_role()** - Get current user's role
4. **is_active_user()** - Check if user account is active

### Business Logic Functions

5. **calculate_user_monthly_meal_cost()** - Calculate total meal cost for a user
   - Supports both fixed and variable pricing
   - Includes guest meal costs
   - Used for financial reporting

6. **is_meal_deadline_passed()** - Check if deadline has passed for a meal
   - Used for deadline enforcement
   - Respects meal_settings configuration

### Trigger Functions

7. **update_updated_at_column()** - Auto-update updated_at timestamp
   - Applied to: users, meals, meal_settings, menu

8. **validate_meal_update()** - Prevent updates to locked meals
   - Enforces deadline restrictions
   - Managers can override

9. **audit_trigger_function()** - Log sensitive operations (optional)
   - Tracks INSERT, UPDATE, DELETE operations
   - Stores old and new data as JSON

---

## Indexes Analysis

### Well-Indexed Tables ✓

All tables have appropriate indexes for common query patterns:

- **Primary Keys**: All tables (UUID)
- **Foreign Keys**: All relationship fields indexed
- **Date Fields**: Indexed DESC for recent-first queries
- **Composite Indexes**: user_id + meal_date on meals table
- **Partial Indexes**:
  - users(role) WHERE is_active = true
  - meals(meal_date) WHERE meal_date >= CURRENT_DATE
  - notifications(user_id) WHERE is_read = false
  - announcements active index with WHERE clause

### Performance Optimizations

✅ **Good Coverage**:
- All foreign keys are indexed
- Date columns use DESC for recent-first ordering
- Boolean filters use partial indexes
- Composite indexes for common JOIN patterns

✅ **No Missing Critical Indexes**:
The migration files include comprehensive indexing. No additional indexes needed for typical workload.

### Potential Future Optimizations (Only if needed)

If the system grows significantly (1000+ students), consider:

1. **Partitioning** meals table by month (if > 100K rows)
2. **Materialized views** for expensive aggregations
3. **Read replicas** for reporting queries (Supabase Pro feature)
4. **Archival strategy** for old data (> 1 year)

**Current verdict**: Schema is well-optimized for expected workload (< 500 students).

---

## Security Model

### Row Level Security (RLS)

All tables have RLS enabled with comprehensive policies:

#### Access Control Matrix

| Table | Students | Managers | Public |
|-------|----------|----------|--------|
| users | Own profile + view other students | All profiles | - |
| meals | Own meals only | All meals | - |
| deposits | Own deposits | All deposits | - |
| expenses | View all (transparency) | All access | - |
| meal_settings | View all | All access | - |
| menu | View all | All access | - |
| announcements | View active | All access | - |
| notifications | Own + broadcast | All access | - |
| audit_log | - | View only | - |

#### Key Security Features

1. **Database-level enforcement** - Cannot be bypassed from client
2. **Role-based access** - Checked via helper functions
3. **Deadline enforcement** - Trigger prevents locked meal changes
4. **Transparency** - Students can view all expenses
5. **Manager override** - Managers can modify locked meals
6. **Audit trail** - Optional logging of sensitive operations

### Storage Security

#### Bucket 1: profile-pictures (Public)
- **Visibility**: Public (anyone can view)
- **Upload**: Authenticated users only
- **Modify/Delete**: Own files only
- **Use case**: User avatars and profile pictures

#### Bucket 2: expense-receipts (Private)
- **Visibility**: Managers only
- **Upload**: Managers only
- **Modify/Delete**: Managers only
- **Use case**: Sensitive financial receipts

### Authentication Security

- Email/password authentication
- JWT with refresh token rotation
- Rate limiting on auth endpoints
- Email confirmation (optional, recommended for production)
- Session management with configurable expiry

---

## Setup Files Provided

### 1. SUPABASE_SETUP.md (28KB, 985 lines)
- **Purpose**: Comprehensive step-by-step setup guide
- **Contents**:
  - Detailed instructions for creating Supabase project
  - How to get and configure credentials
  - Database migration steps
  - Storage bucket setup with policies
  - Authentication configuration
  - Verification steps
  - Security considerations
  - Troubleshooting guide (8 common issues)
  - Production deployment checklist

### 2. SUPABASE_CHECKLIST.md (NEW)
- **Purpose**: Quick reference checklist for setup
- **Contents**:
  - 50+ checkboxes covering all setup steps
  - Quick command reference
  - Common issues & quick fixes
  - Success indicators
  - Estimated time: 15-20 minutes

### 3. TEST_DATA.sql (NEW)
- **Purpose**: Sample data for testing and development
- **Contents**:
  - 1 manager account
  - 5 student accounts with profiles
  - 5+ deposit records (various payment methods)
  - 12+ expense records (all categories)
  - 15 days of past meals (with variation)
  - 7 days of future meals
  - 10 daily menu items
  - 3 announcements (different priorities)
  - Multiple notifications (user-specific and broadcast)
- **Features**:
  - Realistic meal attendance patterns (85-95%)
  - Random guest meals
  - Mixed payment methods
  - Complete coverage of expense categories
  - Demonstrates all features

### 4. Migration Files
- **001_initial_schema.sql** (485 lines)
  - Creates all tables, indexes, views, functions, triggers
  - Includes extensive comments and documentation
  - Sets up default meal settings

- **002_rls_policies.sql** (701 lines)
  - Enables RLS on all tables
  - Creates all security policies
  - Includes storage policy examples
  - Sets up audit logging capability

---

## Quick Start Commands

### 1. First Time Setup

```bash
# 1. Update .env file with your Supabase credentials
# 2. In Supabase SQL Editor, run:
#    - supabase/migrations/001_initial_schema.sql
#    - supabase/migrations/002_rls_policies.sql
# 3. Create storage buckets via UI
# 4. Apply storage policies via SQL Editor
```

### 2. Create First Manager

```sql
-- After registering through the app, run this:
UPDATE users
SET role = 'manager'
WHERE email = 'your-email@example.com';
```

### 3. Load Test Data (Optional)

```sql
-- First register 6 accounts through the app
-- Then run TEST_DATA.sql in SQL Editor
-- Then update manager role as above
```

### 4. Verify Setup

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check RLS is enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';

-- Check policies exist
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

---

## Configuration Requirements

### Environment Variables Required

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Storage Buckets Required

1. **profile-pictures** (public, 2MB limit)
2. **expense-receipts** (private, 5MB limit)

### Initial Data Required

1. At least one manager account
2. Meal settings for current month (auto-created by migration)

---

## Recommendations for the User

### Pre-Setup Recommendations

1. **Read the detailed guide first**: SUPABASE_SETUP.md contains important context
2. **Use the checklist**: SUPABASE_CHECKLIST.md keeps you on track
3. **Save your credentials**: Database password and API keys in a secure location
4. **Use test data**: Load TEST_DATA.sql to explore features before adding real data

### During Setup

1. **Follow the order**: Run migrations in sequence (001 then 002)
2. **Verify each step**: Check tables, buckets, and policies after each phase
3. **Test as you go**: Register account → verify in database → test login
4. **Read error messages**: Migration errors often have helpful details

### Post-Setup

1. **Create manager first**: Update role immediately after registration
2. **Configure settings**: Set meal deadlines and pricing for your hostel
3. **Test with students**: Create test accounts to verify permissions work
4. **Review security**: Check RLS policies prevent unauthorized access

### Production Deployment

1. **Separate projects**: Use different Supabase projects for dev/prod
2. **Enable email confirmation**: Required for production security
3. **Set up backups**: Configure database backup strategy
4. **Monitor usage**: Check Supabase dashboard for errors and performance
5. **Use HTTPS**: Required for production authentication
6. **Enable 2FA**: On your Supabase account for added security

### Optional Enhancements

1. **Custom email templates**: Brand your authentication emails
2. **Audit logging**: Uncomment audit triggers in 002_rls_policies.sql
3. **Database backups**: Set up automated backup schedule
4. **Monitoring**: Implement error tracking (Sentry, etc.)
5. **Performance**: Enable read replicas if needed (paid feature)

---

## Database Schema Diagram (Text)

```
┌─────────────┐
│ auth.users  │ (Supabase managed)
└──────┬──────┘
       │
       │ references
       ↓
┌─────────────┐
│    users    │────────┐
│  (profiles) │        │
└──────┬──────┘        │
       │               │
       │               │ recorded_by
       │               ↓
       │         ┌──────────────┐
       │         │   deposits   │
       │         └──────────────┘
       │
       │         ┌──────────────┐
       │         │   expenses   │
       │         └──────────────┘
       │
       │         ┌──────────────┐
       ├────────→│    meals     │
       │         └──────────────┘
       │
       │         ┌──────────────┐
       ├────────→│notifications │
       │         └──────────────┘
       │
       │         ┌──────────────┐
       └────────→│     menu     │
                 └──────────────┘

┌────────────────┐
│ meal_settings  │ (standalone config)
└────────────────┘

┌────────────────┐
│ announcements  │ (system-wide)
└────────────────┘
```

---

## Support & Resources

### Documentation Files
- **SUPABASE_SETUP.md** - Comprehensive setup guide with troubleshooting
- **SUPABASE_CHECKLIST.md** - Quick reference checklist
- **TEST_DATA.sql** - Sample data for testing
- **This file** - Schema overview and recommendations

### External Resources
- [Supabase Documentation](https://supabase.com/docs)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage Guide](https://supabase.com/docs/guides/storage)
- [Supabase Discord Community](https://discord.supabase.com)

### Migration Files Location
```
supabase/migrations/
├── 001_initial_schema.sql    (485 lines)
└── 002_rls_policies.sql       (701 lines)
```

---

## Statistics

- **Total Tables**: 8 core + 1 optional (audit_log)
- **Total Views**: 4 (for reporting)
- **Total Functions**: 9 (security, business logic, triggers)
- **Total Indexes**: 30+ (including partial and composite)
- **Total Policies**: 40+ RLS policies
- **Migration Lines**: 1,186 total
- **Setup Time**: 15-20 minutes
- **Documentation Pages**: 100+ pages of guides

---

## Final Checklist

Before considering setup complete, verify:

- [ ] All 8 tables exist in database
- [ ] RLS enabled on all tables (check Table Editor)
- [ ] Both storage buckets created with policies
- [ ] Environment variables configured in .env
- [ ] Can register and login to application
- [ ] Manager account created and functional
- [ ] Test student account works with limited access
- [ ] Can upload profile picture
- [ ] Can plan meals as student
- [ ] Can record expenses as manager
- [ ] Financial calculations working correctly

---

**Schema Version**: 1.0.0
**Last Updated**: 2025-10-14
**Compatible With**: Supabase (Latest), PostgreSQL 14+
**Application**: Hostel Meal Management System
