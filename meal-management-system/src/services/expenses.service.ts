import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { Expense, InsertExpense, ExpenseCategory } from '../types/database.types';

/**
 * Get all expenses for a specific month
 */
export const getExpensesByMonth = async (
  month: string
): Promise<ServiceResponse<Expense[]>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
      .select('*')
      .eq('month', month)
      .order('expense_date', { ascending: false });

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
 * Get expenses within a date range
 */
export const getExpensesByDateRange = async (
  startDate: string,
  endDate: string
): Promise<ServiceResponse<Expense[]>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
      .select('*')
      .gte('expense_date', startDate)
      .lte('expense_date', endDate)
      .order('expense_date', { ascending: false });

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
 * Get expenses by category for a specific month
 */
export const getExpensesByCategory = async (
  month: string,
  category: ExpenseCategory
): Promise<ServiceResponse<Expense[]>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
      .select('*')
      .eq('month', month)
      .eq('category', category)
      .order('expense_date', { ascending: false });

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
 * Get a single expense by ID
 */
export const getExpenseById = async (
  id: string
): Promise<ServiceResponse<Expense>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
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
 * Create a new expense
 */
export const createExpense = async (
  expense: InsertExpense
): Promise<ServiceResponse<Expense>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
      .insert(expense)
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
 * Update an expense
 */
export const updateExpense = async (
  id: string,
  updates: Partial<Omit<Expense, 'id' | 'created_at'>>
): Promise<ServiceResponse<Expense>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
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
 * Delete an expense
 */
export const deleteExpense = async (
  id: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase.from('expenses').delete().eq('id', id);

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
 * Get total expenses for a specific month
 */
export const getTotalExpensesByMonth = async (
  month: string
): Promise<ServiceResponse<number>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
      .select('amount')
      .eq('month', month);

    if (error) {
      return createErrorResponse(error.message);
    }

    const total = data?.reduce((sum, expense) => sum + expense.amount, 0) || 0;
    return createSuccessResponse(total);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get expense statistics by category for a month
 */
export const getExpenseStatsByCategory = async (
  month: string
): Promise<ServiceResponse<{ category: ExpenseCategory; total: number; count: number }[]>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
      .select('category, amount')
      .eq('month', month);

    if (error) {
      return createErrorResponse(error.message);
    }

    // Group by category
    const stats = (data || []).reduce((acc, expense) => {
      const category = expense.category || 'other';
      if (!acc[category]) {
        acc[category] = { category, total: 0, count: 0 };
      }
      acc[category].total += expense.amount;
      acc[category].count += 1;
      return acc;
    }, {} as Record<string, { category: ExpenseCategory; total: number; count: number }>);

    return createSuccessResponse(Object.values(stats));
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get recent expenses (last N expenses)
 */
export const getRecentExpenses = async (
  limit: number = 10
): Promise<ServiceResponse<Expense[]>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
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
 * Get expenses recorded by a specific user
 */
export const getExpensesByRecorder = async (
  recordedBy: string,
  month?: string
): Promise<ServiceResponse<Expense[]>> => {
  try {
    let query = supabase
      .from('expenses')
      .select('*')
      .eq('recorded_by', recordedBy)
      .order('expense_date', { ascending: false });

    if (month) {
      query = query.eq('month', month);
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
 * Bulk create expenses
 */
export const bulkCreateExpenses = async (
  expenses: InsertExpense[]
): Promise<ServiceResponse<Expense[]>> => {
  try {
    const { data, error } = await supabase
      .from('expenses')
      .insert(expenses)
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
 * Upload expense receipt
 */
export const uploadExpenseReceipt = async (
  file: File,
  expenseId: string
): Promise<ServiceResponse<string>> => {
  try {
    const fileExt = file.name.split('.').pop();
    const fileName = `${expenseId}-${Date.now()}.${fileExt}`;
    const filePath = `receipts/${fileName}`;

    const { error: uploadError } = await supabase.storage
      .from('expense-receipts')
      .upload(filePath, file);

    if (uploadError) {
      return createErrorResponse(uploadError.message);
    }

    const { data: { publicUrl } } = supabase.storage
      .from('expense-receipts')
      .getPublicUrl(filePath);

    return createSuccessResponse(publicUrl);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Delete expense receipt
 */
export const deleteExpenseReceipt = async (
  receiptUrl: string
): Promise<ServiceResponse<null>> => {
  try {
    // Extract file path from URL
    const url = new URL(receiptUrl);
    const filePath = url.pathname.split('/expense-receipts/')[1];

    if (!filePath) {
      return createErrorResponse('Invalid receipt URL');
    }

    const { error } = await supabase.storage
      .from('expense-receipts')
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
