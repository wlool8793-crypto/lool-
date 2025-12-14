import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. Please check your .env file.'
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
});

// Helper type for service responses
export interface ServiceResponse<T> {
  data: T | null;
  error: string | null;
  success: boolean;
}

// Helper function to create success response
export const createSuccessResponse = <T>(data: T): ServiceResponse<T> => ({
  data,
  error: null,
  success: true,
});

// Helper function to create error response
export const createErrorResponse = <T>(error: string): ServiceResponse<T> => ({
  data: null,
  error,
  success: false,
});
