import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { User, UserRole } from '../types/database.types';

/**
 * Get all users
 */
export const getAllUsers = async (): Promise<ServiceResponse<User[]>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .order('full_name');

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get users by role
 */
export const getUsersByRole = async (
  role: UserRole
): Promise<ServiceResponse<User[]>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('role', role)
      .order('full_name');

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get active users
 */
export const getActiveUsers = async (): Promise<ServiceResponse<User[]>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('is_active', true)
      .order('full_name');

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get user by ID
 */
export const getUserById = async (
  id: string
): Promise<ServiceResponse<User>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get user by email
 */
export const getUserByEmail = async (
  email: string
): Promise<ServiceResponse<User>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('email', email)
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Update user profile
 */
export const updateUserProfile = async (
  id: string,
  updates: Partial<Omit<User, 'id' | 'email' | 'created_at'>>
): Promise<ServiceResponse<User>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Deactivate user
 */
export const deactivateUser = async (
  id: string
): Promise<ServiceResponse<User>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .update({ is_active: false })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Activate user
 */
export const activateUser = async (
  id: string
): Promise<ServiceResponse<User>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .update({ is_active: true })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Delete user (hard delete)
 */
export const deleteUser = async (
  id: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase.from('users').delete().eq('id', id);

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
 * Search users by name or email
 */
export const searchUsers = async (
  searchTerm: string
): Promise<ServiceResponse<User[]>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .or(`full_name.ilike.%${searchTerm}%,email.ilike.%${searchTerm}%`)
      .order('full_name');

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get users by room number
 */
export const getUsersByRoom = async (
  roomNumber: string
): Promise<ServiceResponse<User[]>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('room_number', roomNumber)
      .order('full_name');

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Upload user profile picture
 */
export const uploadProfilePicture = async (
  file: File,
  userId: string
): Promise<ServiceResponse<string>> => {
  try {
    const fileExt = file.name.split('.').pop();
    const fileName = `${userId}-${Date.now()}.${fileExt}`;
    const filePath = `avatars/${fileName}`;

    const { error: uploadError } = await supabase.storage
      .from('profile-pictures')
      .upload(filePath, file);

    if (uploadError) {
      return createErrorResponse(uploadError.message);
    }

    const { data: { publicUrl } } = supabase.storage
      .from('profile-pictures')
      .getPublicUrl(filePath);

    return createSuccessResponse(publicUrl);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Delete user profile picture
 */
export const deleteProfilePicture = async (
  profilePictureUrl: string
): Promise<ServiceResponse<null>> => {
  try {
    // Extract file path from URL
    const url = new URL(profilePictureUrl);
    const filePath = url.pathname.split('/profile-pictures/')[1];

    if (!filePath) {
      return createErrorResponse('Invalid profile picture URL');
    }

    const { error } = await supabase.storage
      .from('profile-pictures')
      .remove([filePath]);

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
 * Get user count by role
 */
export const getUserCountByRole = async (): Promise<
  ServiceResponse<{ role: UserRole; count: number }[]>
> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('role')
      .eq('is_active', true);

    if (error) {
      return createErrorResponse(error.message);
    }

    // Count users by role
    const counts = (data || []).reduce((acc, user) => {
      acc[user.role] = (acc[user.role] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const result = Object.entries(counts).map(([role, count]) => ({
      role: role as UserRole,
      count,
    }));

    return createSuccessResponse(result);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Update user role (manager only)
 */
export const updateUserRole = async (
  userId: string,
  newRole: UserRole
): Promise<ServiceResponse<User>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .update({ role: newRole })
      .eq('id', userId)
      .select()
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};
