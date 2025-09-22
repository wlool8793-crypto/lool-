'use client';

import { useState } from 'react';
import { useExpenses } from '@/hooks/use-expenses';
import { ExpenseForm } from '@/components/expense-form';
import { ExpenseList } from '@/components/expense-list';
import { Dashboard } from '@/components/dashboard';
import { Charts } from '@/components/charts';
import { ExportModal } from '@/components/export-modal';

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
    updateFilters,
  } = useExpenses();

  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Expense Tracker</h1>
          <p className="text-gray-600">Track your expenses and manage your finances</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Dashboard summary={summary} onExportClick={() => setIsExportModalOpen(true)} />
            <Charts expenses={expenses} />
            <ExpenseList
              expenses={expenses}
              onEdit={handleEdit}
              onDelete={deleteExpense}
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

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        expenses={expenses}
      />
    </div>
  );
}
