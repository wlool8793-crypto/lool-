import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, startOfMonth, endOfMonth, isWithinInterval } from 'date-fns';
import { Expense, ExpenseCategory, ExpenseSummary, ExpenseFilters } from '@/types/expense';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM dd, yyyy');
}

export function getMonthRange(date: Date = new Date()) {
  return {
    start: startOfMonth(date),
    end: endOfMonth(date),
  };
}

export function filterExpenses(expenses: Expense[], filters: ExpenseFilters): Expense[] {
  return expenses.filter(expense => {
    if (filters.category && expense.category !== filters.category) {
      return false;
    }

    if (filters.dateRange) {
      const expenseDate = new Date(expense.date);
      if (!isWithinInterval(expenseDate, {
        start: new Date(filters.dateRange.start),
        end: new Date(filters.dateRange.end),
      })) {
        return false;
      }
    }

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      return (
        expense.description.toLowerCase().includes(searchLower) ||
        expense.category.toLowerCase().includes(searchLower)
      );
    }

    return true;
  });
}

export function calculateSummary(expenses: Expense[]): ExpenseSummary {
  const total = expenses.reduce((sum, expense) => sum + expense.amount, 0);

  const currentMonth = getMonthRange();
  const monthlyExpenses = expenses.filter(expense => {
    const expenseDate = new Date(expense.date);
    return isWithinInterval(expenseDate, currentMonth);
  });
  const monthlyTotal = monthlyExpenses.reduce((sum, expense) => sum + expense.amount, 0);

  const categoryTotals = expenses.reduce((acc, expense) => {
    acc[expense.category] = (acc[expense.category] || 0) + expense.amount;
    return acc;
  }, {} as Record<ExpenseCategory, number>);

  const topCategory = Object.entries(categoryTotals).length > 0
    ? Object.entries(categoryTotals).reduce((a, b) => a[1] > b[1] ? a : b)[0] as ExpenseCategory
    : 'Food';

  const averageExpense = expenses.length > 0 ? total / expenses.length : 0;

  return {
    total,
    monthlyTotal,
    categoryTotals,
    topCategory,
    averageExpense,
  };
}

