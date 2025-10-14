-- =============================================
-- HOSTEL MEAL MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- USERS TABLE
-- =============================================
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('manager', 'student')),
  full_name TEXT NOT NULL,
  room_number TEXT,
  phone TEXT,
  profile_picture_url TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- =============================================
-- DEPOSITS TABLE
-- =============================================
CREATE TABLE deposits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
  deposit_date DATE NOT NULL,
  month TEXT NOT NULL, -- Format: 'YYYY-MM'
  payment_method TEXT CHECK (payment_method IN ('cash', 'online', 'upi')),
  notes TEXT,
  recorded_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_deposits_user_id ON deposits(user_id);
CREATE INDEX idx_deposits_month ON deposits(month);
CREATE INDEX idx_deposits_deposit_date ON deposits(deposit_date);

-- =============================================
-- MEALS TABLE
-- =============================================
CREATE TABLE meals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  meal_date DATE NOT NULL,
  breakfast BOOLEAN DEFAULT true,
  lunch BOOLEAN DEFAULT true,
  dinner BOOLEAN DEFAULT true,
  breakfast_locked BOOLEAN DEFAULT false,
  lunch_locked BOOLEAN DEFAULT false,
  dinner_locked BOOLEAN DEFAULT false,
  guest_breakfast INTEGER DEFAULT 0 CHECK (guest_breakfast >= 0),
  guest_lunch INTEGER DEFAULT 0 CHECK (guest_lunch >= 0),
  guest_dinner INTEGER DEFAULT 0 CHECK (guest_dinner >= 0),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, meal_date)
);

-- Indexes
CREATE INDEX idx_meals_user_id ON meals(user_id);
CREATE INDEX idx_meals_meal_date ON meals(meal_date);
CREATE INDEX idx_meals_user_date ON meals(user_id, meal_date);

-- =============================================
-- EXPENSES TABLE
-- =============================================
CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
  expense_date DATE NOT NULL,
  month TEXT NOT NULL, -- Format: 'YYYY-MM'
  category TEXT CHECK (category IN ('vegetables', 'rice', 'meat', 'spices', 'gas', 'utilities', 'other')),
  description TEXT NOT NULL,
  receipt_url TEXT,
  recorded_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_expenses_month ON expenses(month);
CREATE INDEX idx_expenses_expense_date ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category);

-- =============================================
-- MEAL_SETTINGS TABLE
-- =============================================
CREATE TABLE meal_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  month TEXT UNIQUE NOT NULL, -- Format: 'YYYY-MM'
  breakfast_deadline_hour INTEGER DEFAULT 8 CHECK (breakfast_deadline_hour BETWEEN 0 AND 23),
  lunch_deadline_hour INTEGER DEFAULT 13 CHECK (lunch_deadline_hour BETWEEN 0 AND 23),
  dinner_deadline_hour INTEGER DEFAULT 20 CHECK (dinner_deadline_hour BETWEEN 0 AND 23),
  dinner_deadline_previous_day BOOLEAN DEFAULT true,
  fixed_meal_cost DECIMAL(10,2),
  late_cancellation_penalty DECIMAL(10,2) DEFAULT 0,
  guest_meal_price DECIMAL(10,2),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_meal_settings_month ON meal_settings(month);

-- =============================================
-- NOTIFICATIONS TABLE
-- =============================================
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  type TEXT CHECK (type IN ('reminder', 'warning', 'info', 'alert')),
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- =============================================
-- MENU TABLE
-- =============================================
CREATE TABLE menu (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  menu_date DATE NOT NULL,
  breakfast_items TEXT,
  lunch_items TEXT,
  dinner_items TEXT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_menu_date ON menu(menu_date);

-- =============================================
-- ANNOUNCEMENTS TABLE
-- =============================================
CREATE TABLE announcements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  priority TEXT CHECK (priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

-- Index
CREATE INDEX idx_announcements_expires_at ON announcements(expires_at);
CREATE INDEX idx_announcements_created_at ON announcements(created_at DESC);

-- =============================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meals_updated_at BEFORE UPDATE ON meals
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meal_settings_updated_at BEFORE UPDATE ON meal_settings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_menu_updated_at BEFORE UPDATE ON menu
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- HELPER VIEWS
-- =============================================

-- View for meal counts by date
CREATE OR REPLACE VIEW meal_counts_by_date AS
SELECT
  meal_date,
  SUM(CASE WHEN breakfast THEN 1 ELSE 0 END) as breakfast_count,
  SUM(CASE WHEN lunch THEN 1 ELSE 0 END) as lunch_count,
  SUM(CASE WHEN dinner THEN 1 ELSE 0 END) as dinner_count,
  SUM(guest_breakfast) as guest_breakfast_count,
  SUM(guest_lunch) as guest_lunch_count,
  SUM(guest_dinner) as guest_dinner_count
FROM meals
GROUP BY meal_date
ORDER BY meal_date DESC;

-- View for student financial summary
CREATE OR REPLACE VIEW student_financial_summary AS
SELECT
  u.id as user_id,
  u.full_name,
  u.email,
  COALESCE(SUM(d.amount), 0) as total_deposited,
  COUNT(DISTINCT m.id) FILTER (WHERE m.breakfast) as breakfast_count,
  COUNT(DISTINCT m.id) FILTER (WHERE m.lunch) as lunch_count,
  COUNT(DISTINCT m.id) FILTER (WHERE m.dinner) as dinner_count
FROM users u
LEFT JOIN deposits d ON u.id = d.user_id
LEFT JOIN meals m ON u.id = m.user_id
WHERE u.role = 'student' AND u.is_active = true
GROUP BY u.id, u.full_name, u.email;

-- =============================================
-- INSERT DEFAULT SETTINGS
-- =============================================
INSERT INTO meal_settings (month, breakfast_deadline_hour, lunch_deadline_hour, dinner_deadline_hour, dinner_deadline_previous_day)
VALUES (TO_CHAR(CURRENT_DATE, 'YYYY-MM'), 8, 13, 20, true)
ON CONFLICT (month) DO NOTHING;
