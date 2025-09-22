export interface Expense {
  id: string;
  date: string;
  amount: number;
  category: ExpenseCategory;
  description: string;
}

export type ExpenseCategory =
  | 'Food'
  | 'Transportation'
  | 'Entertainment'
  | 'Shopping'
  | 'Bills'
  | 'Other';

export interface ExpenseFormData {
  date: string;
  amount: number;
  category: ExpenseCategory;
  description: string;
}

export interface ExpenseFilters {
  category?: ExpenseCategory;
  dateRange?: {
    start: string;
    end: string;
  };
  search?: string;
}

export interface ExpenseSummary {
  total: number;
  monthlyTotal: number;
  categoryTotals: Record<ExpenseCategory, number>;
  topCategory: ExpenseCategory;
  averageExpense: number;
}