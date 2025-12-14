-- Complete RLS Fix for User Registration
-- This will check and fix all RLS policies on the users table

-- First, let's see what policies exist
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'users';

-- Drop and recreate all policies to ensure they're correct
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile during registration" ON users;
DROP POLICY IF EXISTS "Managers can view all users" ON users;
DROP POLICY IF EXISTS "Managers can insert users" ON users;
DROP POLICY IF EXISTS "Managers can update all users" ON users;
DROP POLICY IF EXISTS "Managers can delete users" ON users;

-- Recreate policies in correct order

-- 1. Allow users to insert their own profile (CRITICAL FOR REGISTRATION)
CREATE POLICY "Users can insert own profile during registration"
  ON users FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- 2. Allow users to view their own profile
CREATE POLICY "Users can view own profile"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- 3. Allow users to update their own profile
CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- 4. Allow managers to view all users
CREATE POLICY "Managers can view all users"
  ON users FOR SELECT
  TO authenticated
  USING (is_manager());

-- 5. Allow managers to insert new users
CREATE POLICY "Managers can insert users"
  ON users FOR INSERT
  TO authenticated
  WITH CHECK (is_manager());

-- 6. Allow managers to update all users
CREATE POLICY "Managers can update all users"
  ON users FOR UPDATE
  TO authenticated
  USING (is_manager())
  WITH CHECK (is_manager());

-- 7. Allow managers to delete users
CREATE POLICY "Managers can delete users"
  ON users FOR DELETE
  TO authenticated
  USING (is_manager());

-- Verify policies were created
SELECT policyname, cmd, permissive
FROM pg_policies
WHERE tablename = 'users'
ORDER BY policyname;
