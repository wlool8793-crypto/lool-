import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { User } from '../types/database.types';

export interface AuthUser {
  id: string;
  email: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role: 'student' | 'manager';
  room_number?: string;
  phone?: string;
}

/**
 * Login with email and password
 */
export const login = async (
  credentials: LoginCredentials
): Promise<ServiceResponse<AuthUser>> => {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: credentials.email,
      password: credentials.password,
    });

    if (error) {
      return createErrorResponse(error.message);
    }

    if (!data.user) {
      return createErrorResponse('Login failed. Please try again.');
    }

    return createSuccessResponse({
      id: data.user.id,
      email: data.user.email!,
    });
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Register a new user
 */
export const register = async (
  userData: RegisterData
): Promise<ServiceResponse<AuthUser>> => {
  try {
    // Create auth user
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email: userData.email,
      password: userData.password,
      options: {
        data: {
          full_name: userData.full_name,
          role: userData.role,
        },
      },
    });

    if (authError) {
      return createErrorResponse(authError.message);
    }

    if (!authData.user) {
      return createErrorResponse('Registration failed. Please try again.');
    }

    // Create user profile in users table
    const { error: profileError } = await supabase.from('users').insert({
      id: authData.user.id,
      email: userData.email,
      full_name: userData.full_name,
      role: userData.role,
      room_number: userData.room_number,
      phone: userData.phone,
      is_active: true,
    });

    if (profileError) {
      // If profile creation fails, we should ideally delete the auth user
      // but Supabase doesn't allow this from client side
      return createErrorResponse(
        `User created but profile setup failed: ${profileError.message}`
      );
    }

    return createSuccessResponse({
      id: authData.user.id,
      email: authData.user.email!,
    });
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Logout current user
 */
export const logout = async (): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase.auth.signOut();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get current authenticated user
 */
export const getCurrentUser = async (): Promise<ServiceResponse<User>> => {
  try {
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError) {
      return createErrorResponse(authError.message);
    }

    if (!user) {
      return createErrorResponse('No authenticated user found');
    }

    // Fetch user profile from users table
    const { data: profile, error: profileError } = await supabase
      .from('users')
      .select('*')
      .eq('id', user.id)
      .single();

    if (profileError) {
      return createErrorResponse(profileError.message);
    }

    if (!profile) {
      return createErrorResponse('User profile not found');
    }

    return createSuccessResponse(profile);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get current auth session
 */
export const getSession = async (): Promise<ServiceResponse<AuthUser | null>> => {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();

    if (error) {
      return createErrorResponse(error.message);
    }

    if (!session) {
      return createSuccessResponse(null);
    }

    return createSuccessResponse({
      id: session.user.id,
      email: session.user.email!,
    });
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Send password reset email
 */
export const resetPassword = async (email: string): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Update user password
 */
export const updatePassword = async (
  newPassword: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    });

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Listen to auth state changes
 */
export const onAuthStateChange = (
  callback: (user: AuthUser | null) => void
) => {
  return supabase.auth.onAuthStateChange((_event, session) => {
    if (session?.user) {
      callback({
        id: session.user.id,
        email: session.user.email!,
      });
    } else {
      callback(null);
    }
  });
};
