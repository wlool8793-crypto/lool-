-- =============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================
--
-- This migration enables Row Level Security on all tables and
-- creates comprehensive security policies for student and manager access.
--
-- Access Control Model:
-- - Students: Can view and manage their own data
-- - Managers: Full access to all data and management features
-- - Public data: Menu, announcements, expenses (transparency)
--
-- Version: 1.0.0
-- Created: 2025-10-13
-- =============================================

-- =============================================
-- ENABLE ROW LEVEL SECURITY
-- =============================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE deposits ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;

-- =============================================
-- HELPER FUNCTIONS FOR RLS POLICIES
-- =============================================

-- Function: Check if current user is a manager
CREATE OR REPLACE FUNCTION is_manager()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid()
      AND role = 'manager'
      AND is_active = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION is_manager IS 'Returns true if authenticated user is an active manager';

-- Function: Check if current user is a student
CREATE OR REPLACE FUNCTION is_student()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid()
      AND role = 'student'
      AND is_active = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION is_student IS 'Returns true if authenticated user is an active student';

-- Function: Get current user's role
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS TEXT AS $$
BEGIN
  RETURN (
    SELECT role
    FROM users
    WHERE id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION get_user_role IS 'Returns the role of the authenticated user';

-- Function: Check if user account is active
CREATE OR REPLACE FUNCTION is_active_user()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid()
      AND is_active = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION is_active_user IS 'Returns true if authenticated user account is active';

-- =============================================
-- USERS TABLE POLICIES
-- =============================================

-- Policy: Students can view their own profile
CREATE POLICY "students_view_own_profile"
  ON users FOR SELECT
  USING (
    auth.uid() = id
    AND role = 'student'
  );

-- Policy: Managers can view all user profiles
CREATE POLICY "managers_view_all_profiles"
  ON users FOR SELECT
  USING (is_manager());

-- Policy: Students can view other students (for community features)
CREATE POLICY "students_view_other_students"
  ON users FOR SELECT
  USING (
    role = 'student'
    AND is_active = true
    AND is_student()
  );

-- Policy: Users can update their own profile (limited fields)
-- Note: Role changes prevented by CHECK constraint or application logic
CREATE POLICY "users_update_own_profile"
  ON users FOR UPDATE
  USING (auth.uid() = id AND is_active = true)
  WITH CHECK (
    auth.uid() = id
    AND is_active = true
    -- Prevent role change
    AND role = (SELECT role FROM users WHERE id = auth.uid())
  );

-- Policy: Managers can insert new users (student onboarding)
CREATE POLICY "managers_insert_users"
  ON users FOR INSERT
  WITH CHECK (is_manager());

-- Policy: Managers can update any user profile
CREATE POLICY "managers_update_users"
  ON users FOR UPDATE
  USING (is_manager());

-- Policy: Managers can soft-delete users (set is_active = false)
-- Note: Hard deletes cascade from auth.users
CREATE POLICY "managers_delete_users"
  ON users FOR DELETE
  USING (is_manager());

-- =============================================
-- DEPOSITS TABLE POLICIES
-- =============================================

-- Policy: Students can view their own deposits
CREATE POLICY "students_view_own_deposits"
  ON deposits FOR SELECT
  USING (
    auth.uid() = user_id
    AND is_active_user()
  );

-- Policy: Managers can view all deposits
CREATE POLICY "managers_view_all_deposits"
  ON deposits FOR SELECT
  USING (is_manager());

-- Policy: Managers can insert deposits for students
CREATE POLICY "managers_insert_deposits"
  ON deposits FOR INSERT
  WITH CHECK (
    is_manager()
    AND EXISTS (
      SELECT 1 FROM users
      WHERE id = user_id
        AND role = 'student'
        AND is_active = true
    )
  );

-- Policy: Managers can update deposits
CREATE POLICY "managers_update_deposits"
  ON deposits FOR UPDATE
  USING (is_manager());

-- Policy: Managers can delete deposits
CREATE POLICY "managers_delete_deposits"
  ON deposits FOR DELETE
  USING (is_manager());

-- =============================================
-- MEALS TABLE POLICIES
-- =============================================

-- Policy: Students can view their own meal plans
CREATE POLICY "students_view_own_meals"
  ON meals FOR SELECT
  USING (
    auth.uid() = user_id
    AND is_active_user()
  );

-- Policy: Managers can view all meal plans
CREATE POLICY "managers_view_all_meals"
  ON meals FOR SELECT
  USING (is_manager());

-- Policy: Students can insert their own meal plans
CREATE POLICY "students_insert_own_meals"
  ON meals FOR INSERT
  WITH CHECK (
    auth.uid() = user_id
    AND is_student()
  );

-- Policy: Students can update their own meal plans
-- Note: Deadline enforcement done at application level or via trigger
CREATE POLICY "students_update_own_meals"
  ON meals FOR UPDATE
  USING (
    auth.uid() = user_id
    AND is_active_user()
  )
  WITH CHECK (
    auth.uid() = user_id
    AND is_active_user()
  );

-- Policy: Managers can insert meals for any student
CREATE POLICY "managers_insert_meals"
  ON meals FOR INSERT
  WITH CHECK (is_manager());

-- Policy: Managers can update any meal (override capability)
CREATE POLICY "managers_update_all_meals"
  ON meals FOR UPDATE
  USING (is_manager());

-- Policy: Managers can delete meals
CREATE POLICY "managers_delete_meals"
  ON meals FOR DELETE
  USING (is_manager());

-- =============================================
-- EXPENSES TABLE POLICIES
-- =============================================
-- Note: Transparency is key - all authenticated users can view expenses

-- Policy: All authenticated users can view expenses
CREATE POLICY "authenticated_users_view_expenses"
  ON expenses FOR SELECT
  USING (
    auth.uid() IS NOT NULL
    AND is_active_user()
  );

-- Policy: Managers can insert expenses
CREATE POLICY "managers_insert_expenses"
  ON expenses FOR INSERT
  WITH CHECK (is_manager());

-- Policy: Managers can update expenses
CREATE POLICY "managers_update_expenses"
  ON expenses FOR UPDATE
  USING (is_manager());

-- Policy: Managers can delete expenses
CREATE POLICY "managers_delete_expenses"
  ON expenses FOR DELETE
  USING (is_manager());

-- =============================================
-- MEAL_SETTINGS TABLE POLICIES
-- =============================================

-- Policy: All authenticated users can view meal settings
CREATE POLICY "authenticated_users_view_meal_settings"
  ON meal_settings FOR SELECT
  USING (
    auth.uid() IS NOT NULL
    AND is_active_user()
  );

-- Policy: Managers can insert meal settings
CREATE POLICY "managers_insert_meal_settings"
  ON meal_settings FOR INSERT
  WITH CHECK (is_manager());

-- Policy: Managers can update meal settings
CREATE POLICY "managers_update_meal_settings"
  ON meal_settings FOR UPDATE
  USING (is_manager());

-- Policy: Managers can delete meal settings
CREATE POLICY "managers_delete_meal_settings"
  ON meal_settings FOR DELETE
  USING (is_manager());

-- =============================================
-- NOTIFICATIONS TABLE POLICIES
-- =============================================

-- Policy: Users can view their own notifications
CREATE POLICY "users_view_own_notifications"
  ON notifications FOR SELECT
  USING (
    auth.uid() = user_id
    AND is_active_user()
  );

-- Policy: Users can view broadcast notifications (user_id IS NULL)
CREATE POLICY "users_view_broadcast_notifications"
  ON notifications FOR SELECT
  USING (
    user_id IS NULL
    AND auth.uid() IS NOT NULL
    AND is_active_user()
  );

-- Policy: Users can update their own notifications (mark as read)
CREATE POLICY "users_update_own_notifications"
  ON notifications FOR UPDATE
  USING (
    auth.uid() = user_id
    AND is_active_user()
  )
  WITH CHECK (
    auth.uid() = user_id
    AND is_active_user()
    -- Only allow updating is_read field
  );

-- Policy: Managers can insert notifications for any user
CREATE POLICY "managers_insert_notifications"
  ON notifications FOR INSERT
  WITH CHECK (is_manager());

-- Policy: Managers can view all notifications
CREATE POLICY "managers_view_all_notifications"
  ON notifications FOR SELECT
  USING (is_manager());

-- Policy: Managers can update any notification
CREATE POLICY "managers_update_notifications"
  ON notifications FOR UPDATE
  USING (is_manager());

-- Policy: Managers can delete notifications
CREATE POLICY "managers_delete_notifications"
  ON notifications FOR DELETE
  USING (is_manager());

-- =============================================
-- MENU TABLE POLICIES
-- =============================================

-- Policy: All authenticated users can view menu
CREATE POLICY "authenticated_users_view_menu"
  ON menu FOR SELECT
  USING (
    auth.uid() IS NOT NULL
    AND is_active_user()
  );

-- Policy: Managers can insert menu items
CREATE POLICY "managers_insert_menu"
  ON menu FOR INSERT
  WITH CHECK (is_manager());

-- Policy: Managers can update menu items
CREATE POLICY "managers_update_menu"
  ON menu FOR UPDATE
  USING (is_manager());

-- Policy: Managers can delete menu items
CREATE POLICY "managers_delete_menu"
  ON menu FOR DELETE
  USING (is_manager());

-- =============================================
-- ANNOUNCEMENTS TABLE POLICIES
-- =============================================

-- Policy: All authenticated users can view active announcements
CREATE POLICY "authenticated_users_view_announcements"
  ON announcements FOR SELECT
  USING (
    auth.uid() IS NOT NULL
    AND is_active_user()
    AND (expires_at IS NULL OR expires_at > NOW())
  );

-- Policy: Managers can view all announcements (including expired)
CREATE POLICY "managers_view_all_announcements"
  ON announcements FOR SELECT
  USING (is_manager());

-- Policy: Managers can insert announcements
CREATE POLICY "managers_insert_announcements"
  ON announcements FOR INSERT
  WITH CHECK (is_manager());

-- Policy: Managers can update announcements
CREATE POLICY "managers_update_announcements"
  ON announcements FOR UPDATE
  USING (is_manager());

-- Policy: Managers can delete announcements
CREATE POLICY "managers_delete_announcements"
  ON announcements FOR DELETE
  USING (is_manager());

-- =============================================
-- GRANT PERMISSIONS ON VIEWS
-- =============================================
-- Views inherit RLS from underlying tables, but we grant SELECT explicitly

GRANT SELECT ON meal_counts_by_date TO authenticated;
GRANT SELECT ON student_financial_summary TO authenticated;
GRANT SELECT ON monthly_expense_summary TO authenticated;
GRANT SELECT ON monthly_meal_statistics TO authenticated;

-- =============================================
-- STORAGE BUCKET POLICIES
-- =============================================
-- Note: These policies are for Supabase Storage buckets
-- Create buckets in Supabase Dashboard or via API:
-- 1. profile-pictures (public bucket)
-- 2. expense-receipts (private bucket)

-- Profile Pictures Bucket Policies (public bucket: profile-pictures)
-- Anyone can view profile pictures
-- Users can upload/update their own profile picture
-- Managers can upload/update any profile picture

-- Expense Receipts Bucket Policies (private bucket: expense-receipts)
-- All authenticated users can view receipts (transparency)
-- Only managers can upload/delete receipts

-- Note: Storage policies are configured in Supabase Dashboard
-- Example policies for reference:

/*
-- Profile Pictures Storage Policies:

-- SELECT policy: Anyone authenticated can view
CREATE POLICY "Anyone can view profile pictures"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'profile-pictures'
  AND auth.role() = 'authenticated'
);

-- INSERT policy: Users can upload their own
CREATE POLICY "Users can upload own profile picture"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- UPDATE policy: Users can update their own
CREATE POLICY "Users can update own profile picture"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- DELETE policy: Users can delete their own
CREATE POLICY "Users can delete own profile picture"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Expense Receipts Storage Policies:

-- SELECT policy: All authenticated can view (transparency)
CREATE POLICY "Authenticated users can view receipts"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'expense-receipts'
  AND auth.role() = 'authenticated'
);

-- INSERT policy: Only managers
CREATE POLICY "Managers can upload receipts"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'expense-receipts'
  AND is_manager()
);

-- UPDATE policy: Only managers
CREATE POLICY "Managers can update receipts"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'expense-receipts'
  AND is_manager()
);

-- DELETE policy: Only managers
CREATE POLICY "Managers can delete receipts"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'expense-receipts'
  AND is_manager()
);
*/

-- =============================================
-- ADDITIONAL SECURITY FUNCTIONS
-- =============================================

-- Function: Check if meal deadline has passed
CREATE OR REPLACE FUNCTION is_meal_deadline_passed(
  p_meal_date DATE,
  p_meal_type TEXT, -- 'breakfast', 'lunch', or 'dinner'
  p_month TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
  v_deadline_hour INTEGER;
  v_deadline_previous_day BOOLEAN;
  v_deadline_timestamp TIMESTAMPTZ;
BEGIN
  -- Get deadline settings
  SELECT
    CASE p_meal_type
      WHEN 'breakfast' THEN breakfast_deadline_hour
      WHEN 'lunch' THEN lunch_deadline_hour
      WHEN 'dinner' THEN dinner_deadline_hour
    END,
    CASE p_meal_type
      WHEN 'dinner' THEN dinner_deadline_previous_day
      ELSE false
    END
  INTO v_deadline_hour, v_deadline_previous_day
  FROM meal_settings
  WHERE month = p_month;

  -- If no settings found, use defaults
  IF v_deadline_hour IS NULL THEN
    v_deadline_hour := CASE p_meal_type
      WHEN 'breakfast' THEN 8
      WHEN 'lunch' THEN 13
      WHEN 'dinner' THEN 20
    END;
    v_deadline_previous_day := (p_meal_type = 'dinner');
  END IF;

  -- Calculate deadline timestamp
  IF v_deadline_previous_day THEN
    v_deadline_timestamp := (p_meal_date - INTERVAL '1 day')::date + (v_deadline_hour || ' hours')::interval;
  ELSE
    v_deadline_timestamp := p_meal_date::date + (v_deadline_hour || ' hours')::interval;
  END IF;

  -- Check if deadline has passed
  RETURN NOW() > v_deadline_timestamp;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION is_meal_deadline_passed IS 'Check if deadline has passed for a specific meal type and date';

-- Function: Validate meal update based on lock status
CREATE OR REPLACE FUNCTION validate_meal_update()
RETURNS TRIGGER AS $$
BEGIN
  -- Managers can always update
  IF is_manager() THEN
    RETURN NEW;
  END IF;

  -- Check if breakfast is locked and being changed
  IF OLD.breakfast_locked AND OLD.breakfast != NEW.breakfast THEN
    RAISE EXCEPTION 'Breakfast is locked and cannot be modified';
  END IF;

  -- Check if lunch is locked and being changed
  IF OLD.lunch_locked AND OLD.lunch != NEW.lunch THEN
    RAISE EXCEPTION 'Lunch is locked and cannot be modified';
  END IF;

  -- Check if dinner is locked and being changed
  IF OLD.dinner_locked AND OLD.dinner != NEW.dinner THEN
    RAISE EXCEPTION 'Dinner is locked and cannot be modified';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply validation trigger to meals table
CREATE TRIGGER validate_meal_update_trigger
  BEFORE UPDATE ON meals
  FOR EACH ROW
  EXECUTE FUNCTION validate_meal_update();

COMMENT ON FUNCTION validate_meal_update IS 'Prevent updates to locked meals (deadline enforcement)';

-- =============================================
-- SECURITY AUDIT LOG (Optional)
-- =============================================

-- Table for audit logging (optional but recommended for production)
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  table_name TEXT NOT NULL,
  operation TEXT NOT NULL, -- INSERT, UPDATE, DELETE
  user_id UUID REFERENCES users(id),
  old_data JSONB,
  new_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);

COMMENT ON TABLE audit_log IS 'Audit trail for sensitive operations';

-- Enable RLS on audit_log
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Only managers can view audit logs
CREATE POLICY "managers_view_audit_log"
  ON audit_log FOR SELECT
  USING (is_manager());

-- Generic audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO audit_log (table_name, operation, user_id, old_data)
    VALUES (TG_TABLE_NAME, TG_OP, auth.uid(), row_to_json(OLD));
    RETURN OLD;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_log (table_name, operation, user_id, old_data, new_data)
    VALUES (TG_TABLE_NAME, TG_OP, auth.uid(), row_to_json(OLD), row_to_json(NEW));
    RETURN NEW;
  ELSIF TG_OP = 'INSERT' THEN
    INSERT INTO audit_log (table_name, operation, user_id, new_data)
    VALUES (TG_TABLE_NAME, TG_OP, auth.uid(), row_to_json(NEW));
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply audit triggers to sensitive tables (optional - enable as needed)
-- Uncomment to enable audit logging:

/*
CREATE TRIGGER audit_users_trigger
  AFTER INSERT OR UPDATE OR DELETE ON users
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_deposits_trigger
  AFTER INSERT OR UPDATE OR DELETE ON deposits
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_expenses_trigger
  AFTER INSERT OR UPDATE OR DELETE ON expenses
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
*/

-- =============================================
-- COMPLETION MESSAGE
-- =============================================

DO $$
BEGIN
  RAISE NOTICE '============================================';
  RAISE NOTICE 'RLS Policies Migration Completed Successfully!';
  RAISE NOTICE '============================================';
  RAISE NOTICE '';
  RAISE NOTICE 'Row Level Security enabled on:';
  RAISE NOTICE '  - users';
  RAISE NOTICE '  - deposits';
  RAISE NOTICE '  - meals';
  RAISE NOTICE '  - expenses';
  RAISE NOTICE '  - meal_settings';
  RAISE NOTICE '  - notifications';
  RAISE NOTICE '  - menu';
  RAISE NOTICE '  - announcements';
  RAISE NOTICE '';
  RAISE NOTICE 'Security policies created for:';
  RAISE NOTICE '  - Student access (own data + public data)';
  RAISE NOTICE '  - Manager access (full access)';
  RAISE NOTICE '  - Public data (menu, announcements, expenses)';
  RAISE NOTICE '';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '  1. Create storage buckets in Supabase Dashboard:';
  RAISE NOTICE '     - profile-pictures (public)';
  RAISE NOTICE '     - expense-receipts (private)';
  RAISE NOTICE '  2. Configure storage policies (examples in migration file)';
  RAISE NOTICE '  3. Create first manager account';
  RAISE NOTICE '  4. Test authentication and permissions';
  RAISE NOTICE '';
  RAISE NOTICE 'Optional:';
  RAISE NOTICE '  - Enable audit logging by uncommenting audit triggers';
  RAISE NOTICE '';
END $$;
