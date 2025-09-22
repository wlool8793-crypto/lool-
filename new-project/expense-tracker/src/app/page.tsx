'use client';

import { useExpenses } from '@/hooks/use-expenses';
import { ExpenseForm } from '@/components/expense-form';
import { ExpenseList } from '@/components/expense-list';
import { Dashboard } from '@/components/dashboard';
import { Charts } from '@/components/charts';

export default function Home() {
  const {
    expenses,
    summary,
    filters,
    editingExpense,
    addExpense,
    updateExpense,
    deleteExpense,
    handleEdit,
    handleCancelEdit,
    handleExport,
    updateFilters,
  } = useExpenses();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Expense Tracker</h1>
          <p className="text-gray-600">Track your expenses and manage your finances</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Dashboard summary={summary} />
            <Charts expenses={expenses} />
            <ExpenseList
              expenses={expenses}
              onEdit={handleEdit}
              onDelete={deleteExpense}
              onExport={handleExport}
              filters={filters}
              onFiltersChange={updateFilters}
            />
          </div>

          <div className="lg:col-span-1">
            <ExpenseForm
              onSubmit={editingExpense
                ? (data) => updateExpense(editingExpense.id, data)
                : addExpense
              }
              editingExpense={editingExpense}
              onCancelEdit={handleCancelEdit}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
