-- =============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE deposits ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;

-- =============================================
-- HELPER FUNCTIONS
-- =============================================

-- Function to check if user is manager
CREATE OR REPLACE FUNCTION is_manager()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid() AND role = 'manager'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is student
CREATE OR REPLACE FUNCTION is_student()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid() AND role = 'student'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user role
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS TEXT AS $$
BEGIN
  RETURN (SELECT role FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================
-- USERS TABLE POLICIES
-- =============================================

-- Students can read their own record
CREATE POLICY "Students can view own profile"
  ON users FOR SELECT
  USING (auth.uid() = id AND role = 'student');

-- Managers can read all records
CREATE POLICY "Managers can view all users"
  ON users FOR SELECT
  USING (is_manager());

-- Managers can update all records
CREATE POLICY "Managers can update all users"
  ON users FOR UPDATE
  USING (is_manager());

-- Managers can insert new students
CREATE POLICY "Managers can insert users"
  ON users FOR INSERT
  WITH CHECK (is_manager());

-- Users can update their own profile (limited fields)
CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

-- =============================================
-- DEPOSITS TABLE POLICIES
-- =============================================

-- Students can read their own deposits
CREATE POLICY "Students can view own deposits"
  ON deposits FOR SELECT
  USING (auth.uid() = user_id);

-- Managers can read all deposits
CREATE POLICY "Managers can view all deposits"
  ON deposits FOR SELECT
  USING (is_manager());

-- Managers can insert deposits
CREATE POLICY "Managers can insert deposits"
  ON deposits FOR INSERT
  WITH CHECK (is_manager());

-- Managers can update deposits
CREATE POLICY "Managers can update deposits"
  ON deposits FOR UPDATE
  USING (is_manager());

-- Managers can delete deposits
CREATE POLICY "Managers can delete deposits"
  ON deposits FOR DELETE
  USING (is_manager());

-- =============================================
-- MEALS TABLE POLICIES
-- =============================================

-- Students can read their own meals
CREATE POLICY "Students can view own meals"
  ON meals FOR SELECT
  USING (auth.uid() = user_id);

-- Managers can read all meals
CREATE POLICY "Managers can view all meals"
  ON meals FOR SELECT
  USING (is_manager());

-- Students can insert their own meals
CREATE POLICY "Students can insert own meals"
  ON meals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Students can update their own meals (with deadline check done in app)
CREATE POLICY "Students can update own meals"
  ON meals FOR UPDATE
  USING (auth.uid() = user_id);

-- Managers can update any meal (override capability)
CREATE POLICY "Managers can update all meals"
  ON meals FOR UPDATE
  USING (is_manager());

-- Managers can delete meals
CREATE POLICY "Managers can delete meals"
  ON meals FOR DELETE
  USING (is_manager());

-- =============================================
-- EXPENSES TABLE POLICIES
-- =============================================

-- All authenticated users can read expenses (transparency)
CREATE POLICY "Anyone can view expenses"
  ON expenses FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- Only managers can insert expenses
CREATE POLICY "Managers can insert expenses"
  ON expenses FOR INSERT
  WITH CHECK (is_manager());

-- Only managers can update expenses
CREATE POLICY "Managers can update expenses"
  ON expenses FOR UPDATE
  USING (is_manager());

-- Only managers can delete expenses
CREATE POLICY "Managers can delete expenses"
  ON expenses FOR DELETE
  USING (is_manager());

-- =============================================
-- MEAL_SETTINGS TABLE POLICIES
-- =============================================

-- Everyone can read meal settings
CREATE POLICY "Anyone can view meal settings"
  ON meal_settings FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- Only managers can insert meal settings
CREATE POLICY "Managers can insert meal settings"
  ON meal_settings FOR INSERT
  WITH CHECK (is_manager());

-- Only managers can update meal settings
CREATE POLICY "Managers can update meal settings"
  ON meal_settings FOR UPDATE
  USING (is_manager());

-- =============================================
-- NOTIFICATIONS TABLE POLICIES
-- =============================================

-- Users can read their own notifications
CREATE POLICY "Users can view own notifications"
  ON notifications FOR SELECT
  USING (auth.uid() = user_id);

-- Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications"
  ON notifications FOR UPDATE
  USING (auth.uid() = user_id);

-- Managers can insert notifications for anyone
CREATE POLICY "Managers can insert notifications"
  ON notifications FOR INSERT
  WITH CHECK (is_manager());

-- Managers can delete notifications
CREATE POLICY "Managers can delete notifications"
  ON notifications FOR DELETE
  USING (is_manager());

-- =============================================
-- MENU TABLE POLICIES
-- =============================================

-- Everyone can read menu
CREATE POLICY "Anyone can view menu"
  ON menu FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- Only managers can insert menu
CREATE POLICY "Managers can insert menu"
  ON menu FOR INSERT
  WITH CHECK (is_manager());

-- Only managers can update menu
CREATE POLICY "Managers can update menu"
  ON menu FOR UPDATE
  USING (is_manager());

-- Only managers can delete menu
CREATE POLICY "Managers can delete menu"
  ON menu FOR DELETE
  USING (is_manager());

-- =============================================
-- ANNOUNCEMENTS TABLE POLICIES
-- =============================================

-- Everyone can read announcements
CREATE POLICY "Anyone can view announcements"
  ON announcements FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- Only managers can insert announcements
CREATE POLICY "Managers can insert announcements"
  ON announcements FOR INSERT
  WITH CHECK (is_manager());

-- Only managers can update announcements
CREATE POLICY "Managers can update announcements"
  ON announcements FOR UPDATE
  USING (is_manager());

-- Only managers can delete announcements
CREATE POLICY "Managers can delete announcements"
  ON announcements FOR DELETE
  USING (is_manager());

-- =============================================
-- GRANT PERMISSIONS ON VIEWS
-- =============================================

GRANT SELECT ON meal_counts_by_date TO authenticated;
GRANT SELECT ON student_financial_summary TO authenticated;
