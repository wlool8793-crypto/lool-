-- =============================================
-- TEST DATA FOR HOSTEL MEAL MANAGEMENT SYSTEM
-- =============================================
--
-- This file contains sample test data for development and testing.
-- Run this in Supabase SQL Editor after completing the migrations.
--
-- IMPORTANT NOTES:
-- 1. Update the email addresses below to real ones you can access
-- 2. You must create auth.users entries first (register through app)
-- 3. After registering, manually update the first user's role to 'manager'
-- 4. This is for TESTING/DEVELOPMENT only - not for production
--
-- Version: 1.0.0
-- Created: 2025-10-14
-- =============================================

-- =============================================
-- INSTRUCTIONS FOR USE
-- =============================================
--
-- STEP 1: Register accounts through your application
-- -----------------------------------------------
-- Register these 6 accounts through the application's registration page:
--
-- Account 1 (Will be Manager):
--   Email: manager@hostel.com
--   Password: Manager@123
--   Full Name: Admin Manager
--
-- Account 2 (Student):
--   Email: john.doe@student.com
--   Password: Student@123
--   Full Name: John Doe
--
-- Account 3 (Student):
--   Email: jane.smith@student.com
--   Password: Student@123
--   Full Name: Jane Smith
--
-- Account 4 (Student):
--   Email: bob.wilson@student.com
--   Password: Student@123
--   Full Name: Bob Wilson
--
-- Account 5 (Student):
--   Email: alice.brown@student.com
--   Password: Student@123
--   Full Name: Alice Brown
--
-- Account 6 (Student):
--   Email: charlie.davis@student.com
--   Password: Student@123
--   Full Name: Charlie Davis
--
-- STEP 2: Update manager role manually
-- -------------------------------------
-- After registration, run this in SQL Editor:
--
-- UPDATE users
-- SET role = 'manager'
-- WHERE email = 'manager@hostel.com';
--
-- STEP 3: Run the rest of this file
-- ----------------------------------
-- Copy and paste everything below this line into SQL Editor and run.
--
-- =============================================

-- =============================================
-- CLEANUP (Optional - only if re-running)
-- =============================================
-- Uncomment these lines if you want to clear existing test data:
/*
DELETE FROM meals WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@student.com' OR email LIKE '%@hostel.com'
);
DELETE FROM deposits WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@student.com' OR email LIKE '%@hostel.com'
);
DELETE FROM expenses;
DELETE FROM menu;
DELETE FROM announcements;
DELETE FROM notifications;
*/

-- =============================================
-- UPDATE USER PROFILES
-- =============================================
-- Add additional profile information to registered users

-- Update manager profile
UPDATE users
SET
  full_name = 'Admin Manager',
  room_number = 'Office-101',
  phone = '+91-9876543210',
  is_active = true
WHERE email = 'manager@hostel.com';

-- Update student profiles
UPDATE users
SET
  full_name = 'John Doe',
  room_number = 'A-201',
  phone = '+91-9876543211',
  is_active = true
WHERE email = 'john.doe@student.com';

UPDATE users
SET
  full_name = 'Jane Smith',
  room_number = 'A-202',
  phone = '+91-9876543212',
  is_active = true
WHERE email = 'jane.smith@student.com';

UPDATE users
SET
  full_name = 'Bob Wilson',
  room_number = 'B-101',
  phone = '+91-9876543213',
  is_active = true
WHERE email = 'bob.wilson@student.com';

UPDATE users
SET
  full_name = 'Alice Brown',
  room_number = 'B-102',
  phone = '+91-9876543214',
  is_active = true
WHERE email = 'alice.brown@student.com';

UPDATE users
SET
  full_name = 'Charlie Davis',
  room_number = 'C-301',
  phone = '+91-9876543215',
  is_active = true
WHERE email = 'charlie.davis@student.com';

-- =============================================
-- MEAL SETTINGS FOR CURRENT AND NEXT MONTH
-- =============================================

-- Settings for current month (if not already exists)
INSERT INTO meal_settings (
  month,
  breakfast_deadline_hour,
  lunch_deadline_hour,
  dinner_deadline_hour,
  dinner_deadline_previous_day,
  fixed_meal_cost,
  late_cancellation_penalty,
  guest_meal_price
)
VALUES (
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  8,      -- Breakfast deadline: 8:00 AM
  13,     -- Lunch deadline: 1:00 PM
  20,     -- Dinner deadline: 8:00 PM
  true,   -- Dinner deadline on previous day
  NULL,   -- No fixed cost (variable based on expenses)
  50.00,  -- Late cancellation penalty: ₹50
  100.00  -- Guest meal price: ₹100
)
ON CONFLICT (month) DO UPDATE
SET
  breakfast_deadline_hour = EXCLUDED.breakfast_deadline_hour,
  lunch_deadline_hour = EXCLUDED.lunch_deadline_hour,
  dinner_deadline_hour = EXCLUDED.dinner_deadline_hour,
  dinner_deadline_previous_day = EXCLUDED.dinner_deadline_previous_day,
  fixed_meal_cost = EXCLUDED.fixed_meal_cost,
  late_cancellation_penalty = EXCLUDED.late_cancellation_penalty,
  guest_meal_price = EXCLUDED.guest_meal_price;

-- Settings for next month
INSERT INTO meal_settings (
  month,
  breakfast_deadline_hour,
  lunch_deadline_hour,
  dinner_deadline_hour,
  dinner_deadline_previous_day,
  fixed_meal_cost,
  late_cancellation_penalty,
  guest_meal_price
)
VALUES (
  TO_CHAR(CURRENT_DATE + INTERVAL '1 month', 'YYYY-MM'),
  8,
  13,
  20,
  true,
  NULL,
  50.00,
  100.00
)
ON CONFLICT (month) DO NOTHING;

-- =============================================
-- DEPOSITS (Student Payments)
-- =============================================

-- John Doe's deposits
INSERT INTO deposits (user_id, amount, deposit_date, month, payment_method, notes, recorded_by)
SELECT
  u.id,
  5000.00,
  CURRENT_DATE - INTERVAL '25 days',
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  'upi',
  'Monthly advance payment',
  m.id
FROM users u
CROSS JOIN users m
WHERE u.email = 'john.doe@student.com'
  AND m.email = 'manager@hostel.com';

-- Jane Smith's deposits
INSERT INTO deposits (user_id, amount, deposit_date, month, payment_method, notes, recorded_by)
SELECT
  u.id,
  6000.00,
  CURRENT_DATE - INTERVAL '25 days',
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  'online',
  'Monthly advance payment',
  m.id
FROM users u
CROSS JOIN users m
WHERE u.email = 'jane.smith@student.com'
  AND m.email = 'manager@hostel.com';

-- Bob Wilson's deposits (two payments)
INSERT INTO deposits (user_id, amount, deposit_date, month, payment_method, notes, recorded_by)
SELECT
  u.id,
  3000.00,
  CURRENT_DATE - INTERVAL '25 days',
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  'cash',
  'First installment',
  m.id
FROM users u
CROSS JOIN users m
WHERE u.email = 'bob.wilson@student.com'
  AND m.email = 'manager@hostel.com';

INSERT INTO deposits (user_id, amount, deposit_date, month, payment_method, notes, recorded_by)
SELECT
  u.id,
  2000.00,
  CURRENT_DATE - INTERVAL '15 days',
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  'cash',
  'Second installment',
  m.id
FROM users u
CROSS JOIN users m
WHERE u.email = 'bob.wilson@student.com'
  AND m.email = 'manager@hostel.com';

-- Alice Brown's deposit
INSERT INTO deposits (user_id, amount, deposit_date, month, payment_method, notes, recorded_by)
SELECT
  u.id,
  5500.00,
  CURRENT_DATE - INTERVAL '20 days',
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  'upi',
  'Monthly advance payment',
  m.id
FROM users u
CROSS JOIN users m
WHERE u.email = 'alice.brown@student.com'
  AND m.email = 'manager@hostel.com';

-- Charlie Davis's deposit
INSERT INTO deposits (user_id, amount, deposit_date, month, payment_method, notes, recorded_by)
SELECT
  u.id,
  4500.00,
  CURRENT_DATE - INTERVAL '18 days',
  TO_CHAR(CURRENT_DATE, 'YYYY-MM'),
  'online',
  'Monthly advance payment',
  m.id
FROM users u
CROSS JOIN users m
WHERE u.email = 'charlie.davis@student.com'
  AND m.email = 'manager@hostel.com';

-- =============================================
-- EXPENSES (Hostel Expenses)
-- =============================================

-- Get manager ID for recorded_by
DO $$
DECLARE
  v_manager_id UUID;
  v_month TEXT;
BEGIN
  SELECT id INTO v_manager_id FROM users WHERE email = 'manager@hostel.com';
  v_month := TO_CHAR(CURRENT_DATE, 'YYYY-MM');

  -- Vegetables expenses
  INSERT INTO expenses (amount, expense_date, month, category, description, recorded_by)
  VALUES
    (1200.00, CURRENT_DATE - INTERVAL '20 days', v_month, 'vegetables', 'Weekly vegetables from local market', v_manager_id),
    (1350.00, CURRENT_DATE - INTERVAL '13 days', v_month, 'vegetables', 'Fresh vegetables - tomatoes, onions, potatoes', v_manager_id),
    (980.00, CURRENT_DATE - INTERVAL '6 days', v_month, 'vegetables', 'Weekly vegetable purchase', v_manager_id);

  -- Rice and grains
  INSERT INTO expenses (amount, expense_date, month, category, description, recorded_by)
  VALUES
    (2500.00, CURRENT_DATE - INTERVAL '22 days', v_month, 'rice', '25kg rice - Basmati', v_manager_id),
    (1800.00, CURRENT_DATE - INTERVAL '10 days', v_month, 'rice', '20kg wheat flour and 10kg rice', v_manager_id);

  -- Meat and protein
  INSERT INTO expenses (amount, expense_date, month, category, description, recorded_by)
  VALUES
    (2200.00, CURRENT_DATE - INTERVAL '18 days', v_month, 'meat', 'Chicken 5kg and fish 3kg', v_manager_id),
    (1500.00, CURRENT_DATE - INTERVAL '11 days', v_month, 'meat', 'Chicken 4kg', v_manager_id),
    (2800.00, CURRENT_DATE - INTERVAL '4 days', v_month, 'meat', 'Mutton 3kg and chicken 4kg', v_manager_id);

  -- Spices and condiments
  INSERT INTO expenses (amount, expense_date, month, category, description, recorded_by)
  VALUES
    (850.00, CURRENT_DATE - INTERVAL '19 days', v_month, 'spices', 'Mixed spices, oil 5L, salt, sugar', v_manager_id),
    (650.00, CURRENT_DATE - INTERVAL '8 days', v_month, 'spices', 'Cooking oil 3L, turmeric, chili powder', v_manager_id);

  -- Gas
  INSERT INTO expenses (amount, expense_date, month, category, description, recorded_by)
  VALUES
    (1900.00, CURRENT_DATE - INTERVAL '15 days', v_month, 'gas', 'LPG cylinder x2', v_manager_id);

  -- Utilities
  INSERT INTO expenses (amount, expense_date, month, category, description, recorded_by)
  VALUES
    (800.00, CURRENT_DATE - INTERVAL '12 days', v_month, 'utilities', 'Kitchen cleaning supplies', v_manager_id),
    (450.00, CURRENT_DATE - INTERVAL '5 days', v_month, 'utilities', 'Dish soap, scrubbers, garbage bags', v_manager_id);

  -- Other
  INSERT INTO expenses (amount, expense_date, month, category, description, recorded_by)
  VALUES
    (600.00, CURRENT_DATE - INTERVAL '16 days', v_month, 'other', 'Kitchen utensils replacement', v_manager_id);

END $$;

-- =============================================
-- MEAL PLANS (Past and Future)
-- =============================================

-- Function to insert meals for a student
DO $$
DECLARE
  v_user RECORD;
  v_date DATE;
  v_days_back INTEGER := 15; -- Generate meals for past 15 days
  v_days_forward INTEGER := 7; -- Generate meals for next 7 days
BEGIN
  -- Loop through each student
  FOR v_user IN (SELECT id, email FROM users WHERE role = 'student' AND email LIKE '%@student.com')
  LOOP
    -- Generate past meals
    FOR i IN 0..v_days_back LOOP
      v_date := CURRENT_DATE - INTERVAL '1 day' * i;

      -- Most students eat most meals, with some variation
      INSERT INTO meals (
        user_id,
        meal_date,
        breakfast,
        lunch,
        dinner,
        breakfast_locked,
        lunch_locked,
        dinner_locked,
        guest_breakfast,
        guest_lunch,
        guest_dinner
      )
      VALUES (
        v_user.id,
        v_date,
        -- Breakfast: 90% attend
        CASE WHEN random() < 0.9 THEN true ELSE false END,
        -- Lunch: 85% attend
        CASE WHEN random() < 0.85 THEN true ELSE false END,
        -- Dinner: 95% attend
        CASE WHEN random() < 0.95 THEN true ELSE false END,
        true, -- All past meals are locked
        true,
        true,
        -- Occasional guest meals
        CASE WHEN random() < 0.1 THEN 1 ELSE 0 END,
        CASE WHEN random() < 0.05 THEN 1 ELSE 0 END,
        CASE WHEN random() < 0.08 THEN 1 ELSE 0 END
      )
      ON CONFLICT (user_id, meal_date) DO NOTHING;
    END LOOP;

    -- Generate future meals (not locked)
    FOR i IN 1..v_days_forward LOOP
      v_date := CURRENT_DATE + INTERVAL '1 day' * i;

      INSERT INTO meals (
        user_id,
        meal_date,
        breakfast,
        lunch,
        dinner,
        breakfast_locked,
        lunch_locked,
        dinner_locked,
        guest_breakfast,
        guest_lunch,
        guest_dinner
      )
      VALUES (
        v_user.id,
        v_date,
        true,  -- Future meals default to true
        true,
        true,
        false, -- Not locked yet
        false,
        false,
        0, -- No guest meals planned yet
        0,
        0
      )
      ON CONFLICT (user_id, meal_date) DO NOTHING;
    END LOOP;
  END LOOP;
END $$;

-- =============================================
-- MENU ITEMS (Sample Daily Menus)
-- =============================================

-- Menu for past week
INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE - INTERVAL '7 days',
  'Idli, Sambar, Coconut Chutney, Tea/Coffee',
  'Rice, Dal Tadka, Mix Veg Curry, Chapati, Pickle, Curd',
  'Rice, Chicken Curry, Aloo Gobi, Chapati, Salad',
  id
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE - INTERVAL '6 days',
  'Poha, Banana, Tea/Coffee',
  'Rice, Rajma Masala, Bhindi Fry, Chapati, Pickle, Buttermilk',
  'Rice, Fish Fry, Dal, Chapati, Salad',
  id
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE - INTERVAL '5 days',
  'Dosa, Potato Masala, Sambar, Coconut Chutney, Tea/Coffee',
  'Rice, Chole Masala, Jeera Aloo, Chapati, Pickle, Curd',
  'Rice, Egg Curry, Mixed Vegetables, Chapati, Papad',
  id
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE - INTERVAL '4 days',
  'Upma, Banana, Tea/Coffee',
  'Rice, Dal Fry, Paneer Butter Masala, Chapati, Pickle, Raita',
  'Rice, Mutton Curry, Cabbage Sabzi, Chapati, Salad',
  id
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE - INTERVAL '3 days',
  'Paratha, Curd, Pickle, Tea/Coffee',
  'Rice, Sambar, Baingan Bharta, Chapati, Pickle, Buttermilk',
  'Rice, Chicken Biryani, Raita, Salad',
  id
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE - INTERVAL '2 days',
  'Bread Omelette, Banana, Tea/Coffee',
  'Rice, Kadhi Pakora, Aloo Matar, Chapati, Pickle, Curd',
  'Rice, Fish Curry, Dal, Chapati, Papad',
  id
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE - INTERVAL '1 day',
  'Idli, Vada, Sambar, Chutney, Tea/Coffee',
  'Rice, Dal Palak, Mix Veg, Chapati, Pickle, Raita',
  'Rice, Egg Masala, Aloo Beans, Chapati, Salad',
  id
FROM users WHERE email = 'manager@hostel.com';

-- Today's menu
INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE,
  'Puri, Chole, Halwa, Tea/Coffee',
  'Rice, Rajma Masala, Gobi Aloo, Chapati, Pickle, Buttermilk',
  'Rice, Chicken Curry, Dal Makhani, Chapati, Salad',
  id
FROM users WHERE email = 'manager@hostel.com'
ON CONFLICT (menu_date) DO NOTHING;

-- Menu for next few days
INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE + INTERVAL '1 day',
  'Dosa, Potato Curry, Sambar, Chutney, Tea/Coffee',
  'Rice, Dal Fry, Paneer Butter Masala, Chapati, Pickle, Curd',
  'Rice, Fish Fry, Mix Veg, Chapati, Papad',
  id
FROM users WHERE email = 'manager@hostel.com'
ON CONFLICT (menu_date) DO NOTHING;

INSERT INTO menu (menu_date, breakfast_items, lunch_items, dinner_items, created_by)
SELECT
  CURRENT_DATE + INTERVAL '2 days',
  'Poha, Banana, Tea/Coffee',
  'Rice, Sambar, Cabbage Poriyal, Chapati, Pickle, Raita',
  'Rice, Mutton Curry, Dal Tadka, Chapati, Salad',
  id
FROM users WHERE email = 'manager@hostel.com'
ON CONFLICT (menu_date) DO NOTHING;

-- =============================================
-- ANNOUNCEMENTS
-- =============================================

INSERT INTO announcements (title, message, priority, created_by, expires_at)
SELECT
  'Welcome to the New Semester!',
  'Welcome all students! We are excited to start this semester. Please ensure you submit your meal deposits by the 5th of each month. For any queries, contact the hostel office.',
  'high',
  id,
  CURRENT_DATE + INTERVAL '30 days'
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO announcements (title, message, priority, created_by, expires_at)
SELECT
  'Meal Timing Update',
  'Please note: Lunch timing has been updated to 12:30 PM - 2:30 PM starting next week. Plan your meals accordingly.',
  'medium',
  id,
  CURRENT_DATE + INTERVAL '15 days'
FROM users WHERE email = 'manager@hostel.com';

INSERT INTO announcements (title, message, priority, created_by, expires_at)
SELECT
  'Special Menu This Weekend',
  'This Sunday, we will have a special menu featuring Chicken Biryani for lunch! Don''t forget to opt in for your meals.',
  'low',
  id,
  CURRENT_DATE + INTERVAL '7 days'
FROM users WHERE email = 'manager@hostel.com';

-- =============================================
-- NOTIFICATIONS
-- =============================================

-- Create reminders for students who haven't planned future meals
DO $$
DECLARE
  v_user RECORD;
BEGIN
  FOR v_user IN (SELECT id, email FROM users WHERE role = 'student' AND email LIKE '%@student.com')
  LOOP
    INSERT INTO notifications (user_id, title, message, type, is_read)
    VALUES (
      v_user.id,
      'Plan Your Meals',
      'Don''t forget to plan your meals for the upcoming week. Deadline is 8 PM the day before!',
      'reminder',
      false
    );
  END LOOP;
END $$;

-- Broadcast notification to all users
INSERT INTO notifications (user_id, title, message, type, is_read)
VALUES (
  NULL, -- Broadcast (NULL user_id)
  'System Maintenance Notice',
  'We will be performing system maintenance this Saturday from 11 PM to 1 AM. The system may be temporarily unavailable.',
  'info',
  false
);

-- Manager-specific notification
INSERT INTO notifications (user_id, title, message, type, is_read)
SELECT
  id,
  'Monthly Report Due',
  'Please prepare the monthly financial report by the end of this week.',
  'alert',
  false
FROM users WHERE email = 'manager@hostel.com';

-- =============================================
-- COMPLETION MESSAGE
-- =============================================

DO $$
BEGIN
  RAISE NOTICE '============================================';
  RAISE NOTICE 'TEST DATA LOADED SUCCESSFULLY!';
  RAISE NOTICE '============================================';
  RAISE NOTICE '';
  RAISE NOTICE 'Summary of test data created:';
  RAISE NOTICE '  - 1 Manager account (manager@hostel.com)';
  RAISE NOTICE '  - 5 Student accounts';
  RAISE NOTICE '  - 5+ Deposit records';
  RAISE NOTICE '  - 12+ Expense records';
  RAISE NOTICE '  - 15 days of past meals + 7 days future meals';
  RAISE NOTICE '  - 10 Daily menu items';
  RAISE NOTICE '  - 3 Announcements';
  RAISE NOTICE '  - Multiple notifications';
  RAISE NOTICE '';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '  1. Verify manager role: UPDATE users SET role = ''manager'' WHERE email = ''manager@hostel.com'';';
  RAISE NOTICE '  2. Log in with manager@hostel.com';
  RAISE NOTICE '  3. Explore the dashboard and features';
  RAISE NOTICE '  4. Test as student by logging in with student accounts';
  RAISE NOTICE '';
  RAISE NOTICE 'Test Accounts:';
  RAISE NOTICE '  Manager: manager@hostel.com / Manager@123';
  RAISE NOTICE '  Student: john.doe@student.com / Student@123';
  RAISE NOTICE '  Student: jane.smith@student.com / Student@123';
  RAISE NOTICE '  Student: bob.wilson@student.com / Student@123';
  RAISE NOTICE '  Student: alice.brown@student.com / Student@123';
  RAISE NOTICE '  Student: charlie.davis@student.com / Student@123';
  RAISE NOTICE '';
  RAISE NOTICE 'REMEMBER: This is test data only!';
  RAISE NOTICE 'For production, use real data and secure passwords.';
  RAISE NOTICE '';
END $$;
