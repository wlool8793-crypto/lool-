-- Fix: Allow users to create their own profile during registration
-- This policy allows authenticated users to insert a row with their own auth.uid()

-- Add policy for user self-registration
CREATE POLICY "Users can insert own profile during registration"
  ON users FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Verify all users policies
-- Expected policies after this migration:
-- 1. Users can view own profile
-- 2. Users can update own profile
-- 3. Users can insert own profile during registration (NEW)
-- 4. Managers can view all users
-- 5. Managers can insert users
-- 6. Managers can update all users
-- 7. Managers can delete users
