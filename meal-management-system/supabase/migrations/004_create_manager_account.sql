-- Create or Update First Manager Account
-- Run this after you've registered your first user

-- Instructions:
-- 1. First, register an account normally at: https://lool-rho.vercel.app/register
-- 2. After registering, run this SQL replacing 'your-email@example.com' with your actual email
-- 3. This will change your role from 'student' to 'manager'

-- Update user role to manager by email
UPDATE users
SET role = 'manager'
WHERE email = 'your-email@example.com'; -- REPLACE WITH YOUR EMAIL

-- Verify the update
SELECT id, email, full_name, role, created_at
FROM users
WHERE email = 'your-email@example.com'; -- REPLACE WITH YOUR EMAIL
