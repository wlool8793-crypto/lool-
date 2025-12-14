# Database Setup Instructions

## Apply Schema to Supabase

Follow these steps to set up your database:

### Option 1: Using Supabase Dashboard (Recommended)

1. Go to your Supabase project: https://ovmdsyzdqmmfokejnyjx.supabase.co

2. Navigate to **SQL Editor** in the left sidebar

3. Create a new query and copy the contents of:
   - First: `supabase/migrations/001_initial_schema.sql`
   - Click **Run** to execute

4. Create another new query and copy the contents of:
   - Second: `supabase/migrations/002_rls_policies.sql`
   - Click **Run** to execute

### Option 2: Using Supabase CLI

```bash
# Install Supabase CLI (if not already installed)
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref ovmdsyzdqmmfokejnyjx

# Apply migrations
supabase db push
```

### Option 3: Manual SQL Execution

Run the following files in order through the SQL Editor:

1. **Initial Schema** (`001_initial_schema.sql`):
   - Creates all tables: users, deposits, meals, expenses, meal_settings, notifications, menu, announcements
   - Sets up indexes for performance
   - Creates triggers for auto-updating timestamps
   - Creates helpful views for reporting

2. **RLS Policies** (`002_rls_policies.sql`):
   - Enables Row Level Security on all tables
   - Creates helper functions (is_manager, is_student)
   - Sets up access policies for students and managers

## After Database Setup

Once the schema is applied, you can:

1. Start the development server:
   ```bash
   cd /workspaces/lool-/meal-management-system
   npm run dev
   ```

2. Create your first manager account by registering through the app

3. The first user you create should be set as a manager in the database (update the `role` field in the `users` table)

## Database Structure

### Core Tables
- **users**: Student and manager accounts
- **deposits**: Student payments/deposits
- **meals**: Daily meal selections (breakfast, lunch, dinner)
- **expenses**: Mess expenses tracking
- **meal_settings**: Deadline settings and pricing per month
- **notifications**: User notifications
- **menu**: Daily menu items
- **announcements**: System-wide announcements

### Security
- Row Level Security (RLS) enabled on all tables
- Students can only access their own data
- Managers have full access to manage the system
- Expenses and menu visible to all authenticated users for transparency
