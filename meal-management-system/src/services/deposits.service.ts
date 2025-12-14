import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { Deposit, InsertDeposit, PaymentMethod } from '../types/database.types';

/**
 * Get all deposits for a specific user
 */
export const getDepositsByUser = async (
  userId: string
): Promise<ServiceResponse<Deposit[]>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('*')
      .eq('user_id', userId)
      .order('deposit_date', { ascending: false });

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
 * Get deposits for a specific user and month
 */
export const getDepositsByUserAndMonth = async (
  userId: string,
  month: string
): Promise<ServiceResponse<Deposit[]>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('*')
      .eq('user_id', userId)
      .eq('month', month)
      .order('deposit_date', { ascending: false });

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
 * Get all deposits for a specific month
 */
export const getDepositsByMonth = async (
  month: string
): Promise<ServiceResponse<Deposit[]>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('*')
      .eq('month', month)
      .order('deposit_date', { ascending: false });

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
 * Get all deposits within a date range
 */
export const getDepositsByDateRange = async (
  startDate: string,
  endDate: string
): Promise<ServiceResponse<Deposit[]>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('*')
      .gte('deposit_date', startDate)
      .lte('deposit_date', endDate)
      .order('deposit_date', { ascending: false });

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
 * Get a single deposit by ID
 */
export const getDepositById = async (
  id: string
): Promise<ServiceResponse<Deposit>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
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
 * Create a new deposit
 */
export const createDeposit = async (
  deposit: InsertDeposit
): Promise<ServiceResponse<Deposit>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .insert(deposit)
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
 * Update a deposit
 */
export const updateDeposit = async (
  id: string,
  updates: Partial<Omit<Deposit, 'id' | 'created_at'>>
): Promise<ServiceResponse<Deposit>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
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
 * Delete a deposit
 */
export const deleteDeposit = async (
  id: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase.from('deposits').delete().eq('id', id);

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
 * Get total deposits for a user in a specific month
 */
export const getTotalDepositsByUserAndMonth = async (
  userId: string,
  month: string
): Promise<ServiceResponse<number>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('amount')
      .eq('user_id', userId)
      .eq('month', month);

    if (error) {
      return createErrorResponse(error.message);
    }

    const total = data?.reduce((sum, deposit) => sum + deposit.amount, 0) || 0;
    return createSuccessResponse(total);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get total deposits for all users in a specific month
 */
export const getTotalDepositsByMonth = async (
  month: string
): Promise<ServiceResponse<number>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('amount')
      .eq('month', month);

    if (error) {
      return createErrorResponse(error.message);
    }

    const total = data?.reduce((sum, deposit) => sum + deposit.amount, 0) || 0;
    return createSuccessResponse(total);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get deposit statistics by payment method for a month
 */
export const getDepositStatsByPaymentMethod = async (
  month: string
): Promise<ServiceResponse<{ method: PaymentMethod; total: number; count: number }[]>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('payment_method, amount')
      .eq('month', month);

    if (error) {
      return createErrorResponse(error.message);
    }

    // Group by payment method
    const stats = (data || []).reduce((acc, deposit) => {
      const method = deposit.payment_method || 'cash';
      if (!acc[method]) {
        acc[method] = { method, total: 0, count: 0 };
      }
      acc[method].total += deposit.amount;
      acc[method].count += 1;
      return acc;
    }, {} as Record<string, { method: PaymentMethod; total: number; count: number }>);

    return createSuccessResponse(Object.values(stats));
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get recent deposits (last N deposits)
 */
export const getRecentDeposits = async (
  limit: number = 10
): Promise<ServiceResponse<Deposit[]>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

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
 * Bulk create deposits
 */
export const bulkCreateDeposits = async (
  deposits: InsertDeposit[]
): Promise<ServiceResponse<Deposit[]>> => {
  try {
    const { data, error } = await supabase
      .from('deposits')
      .insert(deposits)
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
