import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { EmailPreferences } from '../types/email.types';
import { User } from '../types/database.types';

/**
 * Get email preferences for a user
 */
export const getEmailPreferences = async (userId: string): Promise<ServiceResponse<EmailPreferences>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('email_notifications_enabled, meal_reminders, deposit_confirmations, expense_notifications, announcements, daily_summaries, monthly_reports, reminder_hours_before')
      .eq('id', userId)
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    if (!data) {
      return createErrorResponse('User not found');
    }

    const preferences: EmailPreferences = {
      email_notifications_enabled: data.email_notifications_enabled ?? true,
      meal_reminders: data.meal_reminders ?? true,
      deposit_confirmations: data.deposit_confirmations ?? true,
      expense_notifications: data.expense_notifications ?? true,
      announcements: data.announcements ?? true,
      daily_summaries: data.daily_summaries ?? false,
      monthly_reports: data.monthly_reports ?? true,
      reminder_hours_before: data.reminder_hours_before ?? 2,
    };

    return createSuccessResponse(preferences);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to get email preferences'
    );
  }
};

/**
 * Update email preferences for a user
 */
export const updateEmailPreferences = async (
  userId: string,
  preferences: Partial<EmailPreferences>
): Promise<ServiceResponse<EmailPreferences>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .update(preferences)
      .eq('id', userId)
      .select('email_notifications_enabled, meal_reminders, deposit_confirmations, expense_notifications, announcements, daily_summaries, monthly_reports, reminder_hours_before')
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    if (!data) {
      return createErrorResponse('User not found');
    }

    const updatedPreferences: EmailPreferences = {
      email_notifications_enabled: data.email_notifications_enabled ?? true,
      meal_reminders: data.meal_reminders ?? true,
      deposit_confirmations: data.deposit_confirmations ?? true,
      expense_notifications: data.expense_notifications ?? true,
      announcements: data.announcements ?? true,
      daily_summaries: data.daily_summaries ?? false,
      monthly_reports: data.monthly_reports ?? true,
      reminder_hours_before: data.reminder_hours_before ?? 2,
    };

    return createSuccessResponse(updatedPreferences);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to update email preferences'
    );
  }
};

/**
 * Check if user has specific email preference enabled
 */
export const isEmailPreferenceEnabled = async (
  userId: string,
  preference: keyof EmailPreferences
): Promise<ServiceResponse<boolean>> => {
  try {
    const result = await getEmailPreferences(userId);

    if (!result.success || !result.data) {
      return createErrorResponse(result.error || 'Failed to check email preference');
    }

    // If email notifications are disabled globally, return false
    if (!result.data.email_notifications_enabled) {
      return createSuccessResponse(false);
    }

    const isEnabled = result.data[preference] ?? false;
    return createSuccessResponse(!!isEnabled);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to check email preference'
    );
  }
};

/**
 * Get all users with a specific email preference enabled
 */
export const getUsersWithEmailPreferenceEnabled = async (
  preference: keyof Omit<EmailPreferences, 'email_notifications_enabled' | 'reminder_hours_before'>
): Promise<ServiceResponse<User[]>> => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('email_notifications_enabled', true)
      .eq(preference, true)
      .eq('is_active', true);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to get users with email preference'
    );
  }
};

/**
 * Disable all email notifications for a user
 */
export const disableAllEmailNotifications = async (
  userId: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('users')
      .update({ email_notifications_enabled: false })
      .eq('id', userId);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to disable email notifications'
    );
  }
};

/**
 * Enable all email notifications for a user
 */
export const enableAllEmailNotifications = async (
  userId: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('users')
      .update({ email_notifications_enabled: true })
      .eq('id', userId);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to enable email notifications'
    );
  }
};

/**
 * Set default email preferences for a new user
 */
export const setDefaultEmailPreferences = async (
  userId: string
): Promise<ServiceResponse<null>> => {
  try {
    const defaultPreferences: Partial<EmailPreferences> = {
      email_notifications_enabled: true,
      meal_reminders: true,
      deposit_confirmations: true,
      expense_notifications: true,
      announcements: true,
      daily_summaries: false,
      monthly_reports: true,
      reminder_hours_before: 2,
    };

    const { error } = await supabase
      .from('users')
      .update(defaultPreferences)
      .eq('id', userId);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to set default email preferences'
    );
  }
};
