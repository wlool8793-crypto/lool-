import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { Meal, InsertMeal, UpdateMeal } from '../types/database.types';

/**
 * Get all meals for a specific user
 */
export const getMealsByUser = async (
  userId: string,
  startDate?: string,
  endDate?: string
): Promise<ServiceResponse<Meal[]>> => {
  try {
    let query = supabase
      .from('meals')
      .select('*')
      .eq('user_id', userId)
      .order('meal_date', { ascending: false });

    if (startDate) {
      query = query.gte('meal_date', startDate);
    }

    if (endDate) {
      query = query.lte('meal_date', endDate);
    }

    const { data, error } = await query;

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
 * Get meal for a specific user and date
 */
export const getMealByUserAndDate = async (
  userId: string,
  mealDate: string
): Promise<ServiceResponse<Meal | null>> => {
  try {
    const { data, error } = await supabase
      .from('meals')
      .select('*')
      .eq('user_id', userId)
      .eq('meal_date', mealDate)
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
 * Get all meals for a specific date (for managers)
 */
export const getMealsByDate = async (
  mealDate: string
): Promise<ServiceResponse<Meal[]>> => {
  try {
    const { data, error } = await supabase
      .from('meals')
      .select('*')
      .eq('meal_date', mealDate)
      .order('user_id');

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
 * Get all meals within a date range
 */
export const getMealsByDateRange = async (
  startDate: string,
  endDate: string
): Promise<ServiceResponse<Meal[]>> => {
  try {
    const { data, error } = await supabase
      .from('meals')
      .select('*')
      .gte('meal_date', startDate)
      .lte('meal_date', endDate)
      .order('meal_date', { ascending: false });

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
 * Create a new meal entry
 */
export const createMeal = async (
  meal: InsertMeal
): Promise<ServiceResponse<Meal>> => {
  try {
    const { data, error } = await supabase
      .from('meals')
      .insert(meal)
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
 * Update a meal entry
 */
export const updateMeal = async (
  id: string,
  updates: Partial<Omit<Meal, 'id' | 'created_at'>>
): Promise<ServiceResponse<Meal>> => {
  try {
    const { data, error } = await supabase
      .from('meals')
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
 * Upsert a meal entry (create or update)
 */
export const upsertMeal = async (
  meal: InsertMeal
): Promise<ServiceResponse<Meal>> => {
  try {
    const { data, error } = await supabase
      .from('meals')
      .upsert(meal, {
        onConflict: 'user_id,meal_date',
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
 * Delete a meal entry
 */
export const deleteMeal = async (id: string): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase.from('meals').delete().eq('id', id);

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
 * Get meal statistics for a user in a specific month
 */
export const getMealStatsByUserAndMonth = async (
  userId: string,
  month: string
): Promise<ServiceResponse<{
  total_breakfast: number;
  total_lunch: number;
  total_dinner: number;
  total_guest_breakfast: number;
  total_guest_lunch: number;
  total_guest_dinner: number;
}>> => {
  try {
    const { data, error } = await supabase
      .rpc('get_meal_stats_by_user_month', {
        p_user_id: userId,
        p_month: month,
      });

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || {
      total_breakfast: 0,
      total_lunch: 0,
      total_dinner: 0,
      total_guest_breakfast: 0,
      total_guest_lunch: 0,
      total_guest_dinner: 0,
    });
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Check if a meal type is locked for a specific date and user
 */
export const isMealLocked = async (
  userId: string,
  mealDate: string,
  mealType: 'breakfast' | 'lunch' | 'dinner'
): Promise<ServiceResponse<boolean>> => {
  try {
    const { data, error } = await supabase
      .from('meals')
      .select(`${mealType}_locked`)
      .eq('user_id', userId)
      .eq('meal_date', mealDate)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        // No rows returned, meal not locked
        return createSuccessResponse(false);
      }
      return createErrorResponse(error.message);
    }

    const lockField = `${mealType}_locked`;
    const isLocked = data && (data as any)[lockField];
    return createSuccessResponse(Boolean(isLocked));
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Bulk update meal lock status
 */
export const bulkUpdateMealLocks = async (
  mealDate: string,
  mealType: 'breakfast' | 'lunch' | 'dinner',
  locked: boolean
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('meals')
      .update({ [`${mealType}_locked`]: locked })
      .eq('meal_date', mealDate);

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
