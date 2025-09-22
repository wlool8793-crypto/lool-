'use client';

import { useState, useEffect } from 'react';
import { Expense, ExpenseFormData, ExpenseFilters, ExpenseSummary } from '@/types/expense';
import { filterExpenses, calculateSummary } from '@/lib/utils';

const STORAGE_KEY = 'expense-tracker-data';

export function useExpenses() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [filteredExpenses, setFilteredExpenses] = useState<Expense[]>([]);
  const [summary, setSummary] = useState<ExpenseSummary>({
    total: 0,
    monthlyTotal: 0,
    categoryTotals: {
      Food: 0,
      Transportation: 0,
      Entertainment: 0,
      Shopping: 0,
      Bills: 0,
      Other: 0,
    },
    topCategory: 'Food',
    averageExpense: 0,
  });
  const [filters, setFilters] = useState<ExpenseFilters>({});
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);

  useEffect(() => {
    loadExpenses();
  }, []);

  useEffect(() => {
    const filtered = filterExpenses(expenses, filters);
    setFilteredExpenses(filtered);
    setSummary(calculateSummary(expenses));
  }, [expenses, filters]);

  const loadExpenses = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setExpenses(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Error loading expenses:', error);
    }
  };

  const saveExpenses = (newExpenses: Expense[]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newExpenses));
    } catch (error) {
      console.error('Error saving expenses:', error);
    }
  };

  const addExpense = (data: ExpenseFormData) => {
    console.log('addExpense called with data:', data);
    const newExpense: Expense = {
      id: Date.now().toString(),
      ...data,
    };
    console.log('Created new expense:', newExpense);
    const newExpenses = [...expenses, newExpense];
    console.log('New expenses array:', newExpenses);
    setExpenses(newExpenses);
    saveExpenses(newExpenses);
  };

  const updateExpense = (id: string, data: ExpenseFormData) => {
    const newExpenses = expenses.map(expense =>
      expense.id === id ? { ...expense, ...data } : expense
    );
    setExpenses(newExpenses);
    saveExpenses(newExpenses);
    setEditingExpense(null);
  };

  const deleteExpense = (id: string) => {
    const newExpenses = expenses.filter(expense => expense.id !== id);
    setExpenses(newExpenses);
    saveExpenses(newExpenses);
  };

  const handleEdit = (expense: Expense) => {
    setEditingExpense(expense);
  };

  const handleCancelEdit = () => {
    setEditingExpense(null);
  };

  
  const updateFilters = (newFilters: ExpenseFilters) => {
    setFilters(newFilters);
  };

  return {
    expenses: filteredExpenses,
    summary,
    filters,
    editingExpense,
    addExpense,
    updateExpense,
    deleteExpense,
    handleEdit,
    handleCancelEdit,
    updateFilters,
  };
}