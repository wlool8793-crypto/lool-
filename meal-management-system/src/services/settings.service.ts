import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { MealSettings, InsertMealSettings } from '../types/database.types';

/**
 * Get meal settings for a specific month
 */
export const getSettingsByMonth = async (
  month: string
): Promise<ServiceResponse<MealSettings | null>> => {
  try {
    const { data, error } = await supabase
      .from('meal_settings')
      .select('*')
      .eq('month', month)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        // No rows returned
        return createSuccessResponse(null);
      }
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
 * Get current month's settings
 */
export const getCurrentMonthSettings = async (): Promise<
  ServiceResponse<MealSettings | null>
> => {
  try {
    const currentMonth = new Date().toISOString().slice(0, 7); // Format: YYYY-MM
    return getSettingsByMonth(currentMonth);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get all meal settings
 */
export const getAllSettings = async (): Promise<ServiceResponse<MealSettings[]>> => {
  try {
    const { data, error } = await supabase
      .from('meal_settings')
      .select('*')
      .order('month', { ascending: false });

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
 * Get settings by ID
 */
export const getSettingsById = async (
  id: string
): Promise<ServiceResponse<MealSettings>> => {
  try {
    const { data, error } = await supabase
      .from('meal_settings')
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
 * Create new meal settings for a month
 */
export const createSettings = async (
  settings: InsertMealSettings
): Promise<ServiceResponse<MealSettings>> => {
  try {
    const { data, error } = await supabase
      .from('meal_settings')
      .insert(settings)
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
 * Update meal settings
 */
export const updateSettings = async (
  id: string,
  updates: Partial<Omit<MealSettings, 'id' | 'created_at'>>
): Promise<ServiceResponse<MealSettings>> => {
  try {
    const { data, error } = await supabase
      .from('meal_settings')
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
 * Upsert meal settings (create or update based on month)
 */
export const upsertSettings = async (
  settings: InsertMealSettings
): Promise<ServiceResponse<MealSettings>> => {
  try {
    const { data, error } = await supabase
      .from('meal_settings')
      .upsert(settings, {
        onConflict: 'month',
      })
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
 * Delete meal settings
 */
export const deleteSettings = async (
  id: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('meal_settings')
      .delete()
      .eq('id', id);

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
 * Delete settings by month
 */
export const deleteSettingsByMonth = async (
  month: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('meal_settings')
      .delete()
      .eq('month', month);

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
 * Get or create settings for current month with defaults
 */
export const getOrCreateCurrentMonthSettings = async (): Promise<
  ServiceResponse<MealSettings>
> => {
  try {
    const currentMonth = new Date().toISOString().slice(0, 7);

    // Try to get existing settings
    const existingResult = await getSettingsByMonth(currentMonth);

    if (existingResult.success && existingResult.data) {
      return existingResult as ServiceResponse<MealSettings>;
    }

    // Create default settings if none exist
    const defaultSettings: InsertMealSettings = {
      month: currentMonth,
      breakfast_deadline_hour: 20, // 8 PM previous day
      lunch_deadline_hour: 9, // 9 AM same day
      dinner_deadline_hour: 15, // 3 PM same day
      dinner_deadline_previous_day: false,
      late_cancellation_penalty: 10,
      guest_meal_price: 50,
    };

    return createSettings(defaultSettings);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Check if settings exist for a month
 */
export const settingsExistForMonth = async (
  month: string
): Promise<ServiceResponse<boolean>> => {
  try {
    const { count, error } = await supabase
      .from('meal_settings')
      .select('*', { count: 'exact', head: true })
      .eq('month', month);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse((count || 0) > 0);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get settings for multiple months
 */
export const getSettingsByMonthRange = async (
  startMonth: string,
  endMonth: string
): Promise<ServiceResponse<MealSettings[]>> => {
  try {
    const { data, error } = await supabase
      .from('meal_settings')
      .select('*')
      .gte('month', startMonth)
      .lte('month', endMonth)
      .order('month', { ascending: true });

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
 * Copy settings from one month to another
 */
export const copySettingsToMonth = async (
  fromMonth: string,
  toMonth: string
): Promise<ServiceResponse<MealSettings>> => {
  try {
    // Get source settings
    const sourceResult = await getSettingsByMonth(fromMonth);

    if (!sourceResult.success || !sourceResult.data) {
      return createErrorResponse('Source month settings not found');
    }

    // Create new settings with copied values
    const newSettings: InsertMealSettings = {
      month: toMonth,
      breakfast_deadline_hour: sourceResult.data.breakfast_deadline_hour,
      lunch_deadline_hour: sourceResult.data.lunch_deadline_hour,
      dinner_deadline_hour: sourceResult.data.dinner_deadline_hour,
      dinner_deadline_previous_day: sourceResult.data.dinner_deadline_previous_day,
      fixed_meal_cost: sourceResult.data.fixed_meal_cost,
      late_cancellation_penalty: sourceResult.data.late_cancellation_penalty,
      guest_meal_price: sourceResult.data.guest_meal_price,
    };

    return upsertSettings(newSettings);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Subscribe to real-time settings updates
 */
export const subscribeToSettingsUpdates = (
  callback: (settings: MealSettings) => void
) => {
  const channel = supabase
    .channel('meal_settings')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'meal_settings',
      },
      (payload) => {
        if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
          callback(payload.new as MealSettings);
        }
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
};
