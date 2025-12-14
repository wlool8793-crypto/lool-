import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { Menu, InsertMenu } from '../types/database.types';

/**
 * Get menu for a specific date
 */
export const getMenuByDate = async (
  menuDate: string
): Promise<ServiceResponse<Menu | null>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
      .select('*')
      .eq('menu_date', menuDate)
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
 * Get menus for a date range
 */
export const getMenusByDateRange = async (
  startDate: string,
  endDate: string
): Promise<ServiceResponse<Menu[]>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
      .select('*')
      .gte('menu_date', startDate)
      .lte('menu_date', endDate)
      .order('menu_date', { ascending: true });

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
 * Get upcoming menus (next N days)
 */
export const getUpcomingMenus = async (
  days: number = 7
): Promise<ServiceResponse<Menu[]>> => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + days);
    const endDate = futureDate.toISOString().split('T')[0];

    const { data, error } = await supabase
      .from('menus')
      .select('*')
      .gte('menu_date', today)
      .lte('menu_date', endDate)
      .order('menu_date', { ascending: true });

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
 * Get menu by ID
 */
export const getMenuById = async (
  id: string
): Promise<ServiceResponse<Menu>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
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
 * Create a new menu
 */
export const createMenu = async (
  menu: InsertMenu
): Promise<ServiceResponse<Menu>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
      .insert(menu)
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
 * Update a menu
 */
export const updateMenu = async (
  id: string,
  updates: Partial<Omit<Menu, 'id' | 'created_at'>>
): Promise<ServiceResponse<Menu>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
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
 * Upsert a menu (create or update based on date)
 */
export const upsertMenu = async (
  menu: InsertMenu
): Promise<ServiceResponse<Menu>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
      .upsert(menu, {
        onConflict: 'menu_date',
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
 * Delete a menu
 */
export const deleteMenu = async (
  id: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('menus')
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
 * Delete menu by date
 */
export const deleteMenuByDate = async (
  menuDate: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('menus')
      .delete()
      .eq('menu_date', menuDate);

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
 * Bulk create menus
 */
export const bulkCreateMenus = async (
  menus: InsertMenu[]
): Promise<ServiceResponse<Menu[]>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
      .insert(menus)
      .select();

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
 * Get menus created by a specific user
 */
export const getMenusByCreator = async (
  createdBy: string
): Promise<ServiceResponse<Menu[]>> => {
  try {
    const { data, error } = await supabase
      .from('menus')
      .select('*')
      .eq('created_by', createdBy)
      .order('menu_date', { ascending: false });

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
 * Get today's menu
 */
export const getTodayMenu = async (): Promise<ServiceResponse<Menu | null>> => {
  const today = new Date().toISOString().split('T')[0];
  return getMenuByDate(today);
};

/**
 * Get tomorrow's menu
 */
export const getTomorrowMenu = async (): Promise<ServiceResponse<Menu | null>> => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const tomorrowDate = tomorrow.toISOString().split('T')[0];
  return getMenuByDate(tomorrowDate);
};

/**
 * Check if menu exists for a date
 */
export const menuExistsForDate = async (
  menuDate: string
): Promise<ServiceResponse<boolean>> => {
  try {
    const { count, error } = await supabase
      .from('menus')
      .select('*', { count: 'exact', head: true })
      .eq('menu_date', menuDate);

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
 * Subscribe to real-time menu updates
 */
export const subscribeToMenuUpdates = (
  callback: (menu: Menu) => void
) => {
  const channel = supabase
    .channel('menus')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'menus',
      },
      (payload) => {
        if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
          callback(payload.new as Menu);
        }
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
};
