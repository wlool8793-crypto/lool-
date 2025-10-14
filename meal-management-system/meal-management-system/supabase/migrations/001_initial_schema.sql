-- =============================================
-- HOSTEL MEAL MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =============================================
--
-- This migration creates the complete database schema for the
-- Hostel Meal Management System including tables, indexes, views,
-- functions, and triggers.
--
-- Version: 1.0.0
-- Created: 2025-10-13
-- =============================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================
-- USERS TABLE
-- =============================================
-- Stores user profiles for both students and managers
-- References auth.users for authentication integration
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('manager', 'student')),
  full_name TEXT NOT NULL,
  room_number TEXT,
  phone TEXT,
  profile_picture_url TEXT,
  is_active BOOLEAN DEFAULT true NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for performance optimization
CREATE INDEX idx_users_role ON users(role) WHERE is_active = true;
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_email ON users(email);

-- Add comment for documentation
COMMENT ON TABLE users IS 'User profiles for students and managers';
COMMENT ON COLUMN users.role IS 'User role: manager or student';
COMMENT ON COLUMN users.is_active IS 'Whether user account is active';

-- =============================================
-- DEPOSITS TABLE
-- =============================================
-- Tracks student deposits and payments
CREATE TABLE deposits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
  deposit_date DATE NOT NULL DEFAULT CURRENT_DATE,
  month TEXT NOT NULL, -- Format: 'YYYY-MM' e.g., '2025-10'
  payment_method TEXT CHECK (payment_method IN ('cash', 'online', 'upi')),
  notes TEXT,
  recorded_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for efficient querying
CREATE INDEX idx_deposits_user_id ON deposits(user_id);
CREATE INDEX idx_deposits_month ON deposits(month);
CREATE INDEX idx_deposits_deposit_date ON deposits(deposit_date DESC);
CREATE INDEX idx_deposits_recorded_by ON deposits(recorded_by);

-- Add comments
COMMENT ON TABLE deposits IS 'Student deposit and payment records';
COMMENT ON COLUMN deposits.month IS 'Month in YYYY-MM format for grouping deposits';
COMMENT ON COLUMN deposits.recorded_by IS 'Manager who recorded this deposit';

-- =============================================
-- MEALS TABLE
-- =============================================
-- Stores daily meal planning for each student
-- Includes guest meal counts and lock status for deadline enforcement
CREATE TABLE meals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  meal_date DATE NOT NULL,
  breakfast BOOLEAN DEFAULT true NOT NULL,
  lunch BOOLEAN DEFAULT true NOT NULL,
  dinner BOOLEAN DEFAULT true NOT NULL,
  breakfast_locked BOOLEAN DEFAULT false NOT NULL,
  lunch_locked BOOLEAN DEFAULT false NOT NULL,
  dinner_locked BOOLEAN DEFAULT false NOT NULL,
  guest_breakfast INTEGER DEFAULT 0 NOT NULL CHECK (guest_breakfast >= 0 AND guest_breakfast <= 10),
  guest_lunch INTEGER DEFAULT 0 NOT NULL CHECK (guest_lunch >= 0 AND guest_lunch <= 10),
  guest_dinner INTEGER DEFAULT 0 NOT NULL CHECK (guest_dinner >= 0 AND guest_dinner <= 10),
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  UNIQUE(user_id, meal_date)
);

-- Indexes for performance
CREATE INDEX idx_meals_user_id ON meals(user_id);
CREATE INDEX idx_meals_meal_date ON meals(meal_date DESC);
CREATE INDEX idx_meals_user_date ON meals(user_id, meal_date);
CREATE INDEX idx_meals_upcoming ON meals(meal_date) WHERE meal_date >= CURRENT_DATE;

-- Add comments
COMMENT ON TABLE meals IS 'Daily meal planning records for students';
COMMENT ON COLUMN meals.breakfast_locked IS 'Whether breakfast can still be modified (deadline enforcement)';
COMMENT ON COLUMN meals.lunch_locked IS 'Whether lunch can still be modified (deadline enforcement)';
COMMENT ON COLUMN meals.dinner_locked IS 'Whether dinner can still be modified (deadline enforcement)';
COMMENT ON COLUMN meals.guest_breakfast IS 'Number of guest meals for breakfast';

-- =============================================
-- EXPENSES TABLE
-- =============================================
-- Tracks all hostel expenses with receipts
-- Provides transparency for students
CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
  expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
  month TEXT NOT NULL, -- Format: 'YYYY-MM'
  category TEXT CHECK (category IN ('vegetables', 'rice', 'meat', 'spices', 'gas', 'utilities', 'other')),
  description TEXT NOT NULL,
  receipt_url TEXT,
  recorded_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_expenses_month ON expenses(month);
CREATE INDEX idx_expenses_expense_date ON expenses(expense_date DESC);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_recorded_by ON expenses(recorded_by);

-- Add comments
COMMENT ON TABLE expenses IS 'Hostel expense records with receipts';
COMMENT ON COLUMN expenses.month IS 'Month in YYYY-MM format for monthly reports';
COMMENT ON COLUMN expenses.category IS 'Expense category for reporting and analysis';
COMMENT ON COLUMN expenses.receipt_url IS 'URL to receipt image in storage bucket';

-- =============================================
-- MEAL_SETTINGS TABLE
-- =============================================
-- Configurable settings for meal deadlines, pricing, and penalties
-- One record per month for flexible configuration
CREATE TABLE meal_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  month TEXT UNIQUE NOT NULL, -- Format: 'YYYY-MM'
  breakfast_deadline_hour INTEGER DEFAULT 8 NOT NULL CHECK (breakfast_deadline_hour BETWEEN 0 AND 23),
  lunch_deadline_hour INTEGER DEFAULT 13 NOT NULL CHECK (lunch_deadline_hour BETWEEN 0 AND 23),
  dinner_deadline_hour INTEGER DEFAULT 20 NOT NULL CHECK (dinner_deadline_hour BETWEEN 0 AND 23),
  dinner_deadline_previous_day BOOLEAN DEFAULT true NOT NULL,
  fixed_meal_cost DECIMAL(10,2) CHECK (fixed_meal_cost >= 0),
  late_cancellation_penalty DECIMAL(10,2) DEFAULT 0 NOT NULL CHECK (late_cancellation_penalty >= 0),
  guest_meal_price DECIMAL(10,2) CHECK (guest_meal_price >= 0),
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index
CREATE INDEX idx_meal_settings_month ON meal_settings(month);

-- Add comments
COMMENT ON TABLE meal_settings IS 'Monthly meal settings for deadlines and pricing';
COMMENT ON COLUMN meal_settings.breakfast_deadline_hour IS 'Hour (0-23) when breakfast planning locks';
COMMENT ON COLUMN meal_settings.lunch_deadline_hour IS 'Hour (0-23) when lunch planning locks';
COMMENT ON COLUMN meal_settings.dinner_deadline_hour IS 'Hour (0-23) when dinner planning locks';
COMMENT ON COLUMN meal_settings.dinner_deadline_previous_day IS 'If true, dinner deadline is on previous day';
COMMENT ON COLUMN meal_settings.fixed_meal_cost IS 'Optional fixed cost per meal (if not variable)';
COMMENT ON COLUMN meal_settings.late_cancellation_penalty IS 'Penalty amount for late cancellations';
COMMENT ON COLUMN meal_settings.guest_meal_price IS 'Fixed price per guest meal';

-- =============================================
-- NOTIFICATIONS TABLE
-- =============================================
-- System notifications for users
-- Can be user-specific or broadcast to all
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  type TEXT CHECK (type IN ('reminder', 'warning', 'info', 'alert')) DEFAULT 'info',
  is_read BOOLEAN DEFAULT false NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id) WHERE is_read = false;
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_type ON notifications(type);

-- Add comments
COMMENT ON TABLE notifications IS 'User notifications for reminders and alerts';
COMMENT ON COLUMN notifications.user_id IS 'Target user (NULL for broadcast notifications)';
COMMENT ON COLUMN notifications.type IS 'Notification type: reminder, warning, info, or alert';

-- =============================================
-- MENU TABLE
-- =============================================
-- Daily meal menus for breakfast, lunch, and dinner
CREATE TABLE menu (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  menu_date DATE UNIQUE NOT NULL,
  breakfast_items TEXT,
  lunch_items TEXT,
  dinner_items TEXT,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_menu_date ON menu(menu_date DESC);
CREATE INDEX idx_menu_upcoming ON menu(menu_date) WHERE menu_date >= CURRENT_DATE;
CREATE INDEX idx_menu_created_by ON menu(created_by);

-- Add comments
COMMENT ON TABLE menu IS 'Daily meal menus';
COMMENT ON COLUMN menu.menu_date IS 'Date for this menu';
COMMENT ON COLUMN menu.breakfast_items IS 'Comma-separated breakfast items';
COMMENT ON COLUMN menu.lunch_items IS 'Comma-separated lunch items';
COMMENT ON COLUMN menu.dinner_items IS 'Comma-separated dinner items';

-- =============================================
-- ANNOUNCEMENTS TABLE
-- =============================================
-- System-wide announcements from managers
CREATE TABLE announcements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  priority TEXT CHECK (priority IN ('low', 'medium', 'high')) DEFAULT 'medium' NOT NULL,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  expires_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_announcements_expires_at ON announcements(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_announcements_created_at ON announcements(created_at DESC);
CREATE INDEX idx_announcements_priority ON announcements(priority);
CREATE INDEX idx_announcements_active ON announcements(created_at, expires_at)
  WHERE expires_at IS NULL OR expires_at > NOW();

-- Add comments
COMMENT ON TABLE announcements IS 'System announcements from managers';
COMMENT ON COLUMN announcements.priority IS 'Priority level: low, medium, or high';
COMMENT ON COLUMN announcements.expires_at IS 'Optional expiration date for announcement';

-- =============================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================
-- Automatically update updated_at timestamp on record changes

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at column
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meals_updated_at
  BEFORE UPDATE ON meals
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meal_settings_updated_at
  BEFORE UPDATE ON meal_settings
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_menu_updated_at
  BEFORE UPDATE ON menu
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- UTILITY FUNCTIONS
-- =============================================

-- Function to calculate total meal cost for a user in a month
CREATE OR REPLACE FUNCTION calculate_user_monthly_meal_cost(
  p_user_id UUID,
  p_month TEXT
)
RETURNS DECIMAL AS $$
DECLARE
  v_total_meals INTEGER;
  v_total_expenses DECIMAL;
  v_fixed_cost DECIMAL;
  v_guest_cost DECIMAL;
  v_cost_per_meal DECIMAL;
  v_user_meals INTEGER;
  v_user_guest_meals INTEGER;
  v_guest_meal_price DECIMAL;
BEGIN
  -- Get settings for the month
  SELECT fixed_meal_cost, guest_meal_price
  INTO v_fixed_cost, v_guest_meal_price
  FROM meal_settings
  WHERE month = p_month;

  -- If using fixed cost
  IF v_fixed_cost IS NOT NULL THEN
    -- Count user's meals
    SELECT
      COALESCE(SUM((breakfast::int + lunch::int + dinner::int)), 0),
      COALESCE(SUM(guest_breakfast + guest_lunch + guest_dinner), 0)
    INTO v_user_meals, v_user_guest_meals
    FROM meals
    WHERE user_id = p_user_id
      AND TO_CHAR(meal_date, 'YYYY-MM') = p_month;

    RETURN (v_user_meals * v_fixed_cost) + (v_user_guest_meals * COALESCE(v_guest_meal_price, v_fixed_cost));
  END IF;

  -- Variable cost calculation
  -- Get total expenses for the month
  SELECT COALESCE(SUM(amount), 0)
  INTO v_total_expenses
  FROM expenses
  WHERE month = p_month;

  -- Get total meals for all users
  SELECT COALESCE(SUM(breakfast::int + lunch::int + dinner::int), 0)
  INTO v_total_meals
  FROM meals
  WHERE TO_CHAR(meal_date, 'YYYY-MM') = p_month;

  -- If no meals yet, return 0
  IF v_total_meals = 0 THEN
    RETURN 0;
  END IF;

  -- Calculate cost per meal
  v_cost_per_meal := v_total_expenses / v_total_meals;

  -- Get user's meal count
  SELECT
    COALESCE(SUM((breakfast::int + lunch::int + dinner::int)), 0),
    COALESCE(SUM(guest_breakfast + guest_lunch + guest_dinner), 0)
  INTO v_user_meals, v_user_guest_meals
  FROM meals
  WHERE user_id = p_user_id
    AND TO_CHAR(meal_date, 'YYYY-MM') = p_month;

  -- Calculate guest meal cost
  v_guest_cost := v_user_guest_meals * COALESCE(v_guest_meal_price, v_cost_per_meal);

  RETURN (v_user_meals * v_cost_per_meal) + v_guest_cost;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_user_monthly_meal_cost IS 'Calculate total meal cost for a user in a given month';

-- =============================================
-- VIEWS FOR REPORTING AND ANALYTICS
-- =============================================

-- View: Meal counts by date
-- Aggregates meal counts for reporting and kitchen planning
CREATE OR REPLACE VIEW meal_counts_by_date AS
SELECT
  meal_date,
  COUNT(DISTINCT user_id) as total_students,
  SUM(CASE WHEN breakfast THEN 1 ELSE 0 END)::INTEGER as breakfast_count,
  SUM(CASE WHEN lunch THEN 1 ELSE 0 END)::INTEGER as lunch_count,
  SUM(CASE WHEN dinner THEN 1 ELSE 0 END)::INTEGER as dinner_count,
  SUM(guest_breakfast)::INTEGER as guest_breakfast_count,
  SUM(guest_lunch)::INTEGER as guest_lunch_count,
  SUM(guest_dinner)::INTEGER as guest_dinner_count,
  (SUM(CASE WHEN breakfast THEN 1 ELSE 0 END) + SUM(guest_breakfast))::INTEGER as total_breakfast,
  (SUM(CASE WHEN lunch THEN 1 ELSE 0 END) + SUM(guest_lunch))::INTEGER as total_lunch,
  (SUM(CASE WHEN dinner THEN 1 ELSE 0 END) + SUM(guest_dinner))::INTEGER as total_dinner
FROM meals
GROUP BY meal_date
ORDER BY meal_date DESC;

COMMENT ON VIEW meal_counts_by_date IS 'Aggregated meal counts by date for reporting';

-- View: Student financial summary
-- Comprehensive financial overview for each student
CREATE OR REPLACE VIEW student_financial_summary AS
SELECT
  u.id as user_id,
  u.full_name,
  u.email,
  u.room_number,
  COALESCE(SUM(d.amount), 0) as total_deposited,
  COUNT(DISTINCT m.id) FILTER (WHERE m.breakfast) as breakfast_count,
  COUNT(DISTINCT m.id) FILTER (WHERE m.lunch) as lunch_count,
  COUNT(DISTINCT m.id) FILTER (WHERE m.dinner) as dinner_count,
  (COUNT(DISTINCT m.id) FILTER (WHERE m.breakfast) +
   COUNT(DISTINCT m.id) FILTER (WHERE m.lunch) +
   COUNT(DISTINCT m.id) FILTER (WHERE m.dinner))::INTEGER as total_meal_count,
  COALESCE(SUM(m.guest_breakfast), 0)::INTEGER as total_guest_breakfast,
  COALESCE(SUM(m.guest_lunch), 0)::INTEGER as total_guest_lunch,
  COALESCE(SUM(m.guest_dinner), 0)::INTEGER as total_guest_dinner,
  (COALESCE(SUM(m.guest_breakfast), 0) +
   COALESCE(SUM(m.guest_lunch), 0) +
   COALESCE(SUM(m.guest_dinner), 0))::INTEGER as total_guest_meals,
  MAX(d.deposit_date) as last_deposit_date,
  MAX(m.meal_date) as last_meal_date
FROM users u
LEFT JOIN deposits d ON u.id = d.user_id
LEFT JOIN meals m ON u.id = m.user_id
WHERE u.role = 'student' AND u.is_active = true
GROUP BY u.id, u.full_name, u.email, u.room_number
ORDER BY u.full_name;

COMMENT ON VIEW student_financial_summary IS 'Financial summary for each active student';

-- View: Monthly expense summary
-- Summarizes expenses by month and category
CREATE OR REPLACE VIEW monthly_expense_summary AS
SELECT
  month,
  category,
  COUNT(*) as expense_count,
  SUM(amount) as total_amount,
  AVG(amount) as average_amount,
  MIN(amount) as min_amount,
  MAX(amount) as max_amount
FROM expenses
GROUP BY month, category
ORDER BY month DESC, total_amount DESC;

COMMENT ON VIEW monthly_expense_summary IS 'Expense summary grouped by month and category';

-- View: Monthly meal statistics
-- Overall meal statistics by month
CREATE OR REPLACE VIEW monthly_meal_statistics AS
SELECT
  TO_CHAR(meal_date, 'YYYY-MM') as month,
  COUNT(DISTINCT user_id) as unique_students,
  SUM(CASE WHEN breakfast THEN 1 ELSE 0 END)::INTEGER as total_breakfasts,
  SUM(CASE WHEN lunch THEN 1 ELSE 0 END)::INTEGER as total_lunches,
  SUM(CASE WHEN dinner THEN 1 ELSE 0 END)::INTEGER as total_dinners,
  SUM((breakfast::int + lunch::int + dinner::int))::INTEGER as total_meals,
  SUM(guest_breakfast + guest_lunch + guest_dinner)::INTEGER as total_guest_meals,
  AVG((breakfast::int + lunch::int + dinner::int)) as avg_meals_per_student_per_day
FROM meals
GROUP BY TO_CHAR(meal_date, 'YYYY-MM')
ORDER BY month DESC;

COMMENT ON VIEW monthly_meal_statistics IS 'Aggregated meal statistics by month';

-- =============================================
-- INSERT DEFAULT DATA
-- =============================================

-- Insert default meal settings for current month
INSERT INTO meal_settings (
  month,
  breakfast_deadline_hour,
  lunch_deadline_hour,
  dinner_deadline_hour,
  dinner_deadline_previous_day,
  late_cancellation_penalty
)
VALUES (
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  8,    -- 8:00 AM
  13,   -- 1:00 PM
  20,   -- 8:00 PM
  true, -- Dinner deadline on previous day
  0     -- No penalty by default
)
ON CONFLICT (month) DO NOTHING;

-- =============================================
-- COMPLETION MESSAGE
-- =============================================
DO $$
BEGIN
  RAISE NOTICE 'Initial schema migration completed successfully!';
  RAISE NOTICE 'Tables created: users, deposits, meals, expenses, meal_settings, notifications, menu, announcements';
  RAISE NOTICE 'Views created: meal_counts_by_date, student_financial_summary, monthly_expense_summary, monthly_meal_statistics';
  RAISE NOTICE 'Next step: Run 002_rls_policies.sql to enable Row Level Security';
END $$;
