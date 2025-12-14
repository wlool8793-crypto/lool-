-- =====================================================
-- STORAGE BUCKET POLICIES FOR MEAL MANAGEMENT SYSTEM
-- =====================================================
-- Run this script in Supabase SQL Editor AFTER creating the buckets
-- This script sets up security policies for file uploads/access

-- =====================================================
-- PROFILE PICTURES BUCKET POLICIES
-- =====================================================

-- Allow authenticated users to upload their profile pictures
CREATE POLICY "Allow authenticated users to upload profile pictures"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow public to view all profile pictures
CREATE POLICY "Allow public to view profile pictures"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'profile-pictures');

-- Allow users to update their own profile pictures
CREATE POLICY "Allow users to update own profile pictures"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow users to delete their own profile pictures
CREATE POLICY "Allow users to delete own profile pictures"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'profile-pictures'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- =====================================================
-- EXPENSE RECEIPTS BUCKET POLICIES
-- =====================================================

-- Allow managers to upload expense receipts
CREATE POLICY "Allow managers to upload expense receipts"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'expense-receipts'
  AND EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid()
    AND role = 'manager'
  )
);

-- Allow managers to view all expense receipts
CREATE POLICY "Allow managers to view expense receipts"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid()
    AND role = 'manager'
  )
);

-- Allow managers to update expense receipts
CREATE POLICY "Allow managers to update expense receipts"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid()
    AND role = 'manager'
  )
);

-- Allow managers to delete expense receipts
CREATE POLICY "Allow managers to delete expense receipts"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'expense-receipts'
  AND EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid()
    AND role = 'manager'
  )
);

-- =====================================================
-- VERIFICATION QUERY
-- =====================================================
-- Run this after applying policies to verify they were created:

SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd
FROM pg_policies
WHERE tablename = 'objects'
AND schemaname = 'storage'
ORDER BY policyname;
