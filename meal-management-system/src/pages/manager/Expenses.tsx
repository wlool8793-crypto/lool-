import React, { useState, useEffect } from 'react';
import {
  Plus,
  Download,
  Filter,
  DollarSign,
  Calendar,
  Tag,
  FileText,
  Upload,
  X,
  Trash2,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
import { Button } from '../../components/forms/Button';
import { Input } from '../../components/forms/Input';
import { Select } from '../../components/forms/Select';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import {
  getExpensesByMonth,
  getExpensesByDateRange,
  createExpense,
  deleteExpense,
  uploadExpenseReceipt,
  getTotalExpensesByMonth,
  getExpenseStatsByCategory,
} from '../../services/expenses.service';
import { Expense, ExpenseCategory, InsertExpense } from '../../types/database.types';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

interface CategoryStat {
  category: ExpenseCategory;
  total: number;
  count: number;
}

export const Expenses: React.FC = () => {
  const { user } = useAuth();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [totalExpenses, setTotalExpenses] = useState(0);
  const [categoryStats, setCategoryStats] = useState<CategoryStat[]>([]);

  // Filters
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  // Form state
  const [formData, setFormData] = useState<InsertExpense>({
    amount: 0,
    expense_date: new Date().toISOString().split('T')[0],
    month: new Date().toISOString().slice(0, 7),
    category: 'other',
    description: '',
    recorded_by: user?.id || '',
  });
  const [receiptFile, setReceiptFile] = useState<File | null>(null);

  const categoryOptions = [
    { value: 'all', label: 'All Categories' },
    { value: 'vegetables', label: 'Vegetables' },
    { value: 'rice', label: 'Rice' },
    { value: 'meat', label: 'Meat' },
    { value: 'spices', label: 'Spices' },
    { value: 'gas', label: 'Gas' },
    { value: 'utilities', label: 'Utilities' },
    { value: 'other', label: 'Other' },
  ];

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      let result;

      if (startDate && endDate) {
        result = await getExpensesByDateRange(startDate, endDate);
      } else {
        result = await getExpensesByMonth(selectedMonth);
      }

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch expenses');
      }

      let expensesList = result.data || [];

      // Apply category filter
      if (categoryFilter !== 'all') {
        expensesList = expensesList.filter((e) => e.category === categoryFilter);
      }

      setExpenses(expensesList);

      // Fetch total and stats
      const totalResult = await getTotalExpensesByMonth(selectedMonth);
      if (totalResult.success) {
        setTotalExpenses(totalResult.data || 0);
      }

      const statsResult = await getExpenseStatsByCategory(selectedMonth);
      if (statsResult.success) {
        setCategoryStats(statsResult.data || []);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch expenses');
    } finally {
      setLoading(false);
    }
  };

  const handleAddExpense = async () => {
    if (!formData.amount || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    setActionLoading('add');
    try {
      // Create expense
      const result = await createExpense(formData);

      if (!result.success) {
        throw new Error(result.error || 'Failed to create expense');
      }

      // Upload receipt if provided
      if (receiptFile && result.data) {
        const uploadResult = await uploadExpenseReceipt(receiptFile, result.data.id);
        if (!uploadResult.success) {
          toast.error('Expense added but receipt upload failed');
        }
      }

      toast.success('Expense added successfully');
      setShowAddModal(false);
      resetForm();
      await fetchExpenses();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to add expense');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteExpense = async (id: string) => {
    if (!confirm('Are you sure you want to delete this expense?')) {
      return;
    }

    setActionLoading(id);
    try {
      const result = await deleteExpense(id);

      if (!result.success) {
        throw new Error(result.error || 'Failed to delete expense');
      }

      toast.success('Expense deleted successfully');
      await fetchExpenses();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to delete expense');
    } finally {
      setActionLoading(null);
    }
  };

  const handleExport = () => {
    const headers = ['Date', 'Category', 'Amount', 'Description'];
    const rows = expenses.map((e) => [
      e.expense_date,
      e.category || 'N/A',
      e.amount.toFixed(2),
      e.description,
    ]);

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `expenses-${selectedMonth}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const resetForm = () => {
    setFormData({
      amount: 0,
      expense_date: new Date().toISOString().split('T')[0],
      month: new Date().toISOString().slice(0, 7),
      category: 'other',
      description: '',
      recorded_by: user?.id || '',
    });
    setReceiptFile(null);
  };

  useEffect(() => {
    if (user) {
      setFormData((prev) => ({ ...prev, recorded_by: user.id }));
    }
  }, [user]);

  useEffect(() => {
    fetchExpenses();
  }, [selectedMonth, startDate, endDate, categoryFilter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Expense Management</h1>
          <p className="text-gray-600 mt-1">Track and manage all hostel expenses</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleExport} leftIcon={<Download className="w-4 h-4" />}>
            Export CSV
          </Button>
          <Button onClick={() => setShowAddModal(true)} leftIcon={<Plus className="w-4 h-4" />}>
            Add Expense
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">${totalExpenses.toFixed(2)}</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-3">
              <DollarSign className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Items</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{expenses.length}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Categories</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{categoryStats.length}</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <Tag className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg per Day</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${expenses.length > 0 ? (totalExpenses / new Date().getDate()).toFixed(2) : '0.00'}
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-3">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Input
            type="month"
            label="Month"
            value={selectedMonth}
            onChange={(e) => {
              setSelectedMonth(e.target.value);
              setStartDate('');
              setEndDate('');
            }}
            leftIcon={<Calendar className="w-5 h-5" />}
          />
          <Input
            type="date"
            label="Start Date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            placeholder="Start date"
          />
          <Input
            type="date"
            label="End Date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            placeholder="End date"
          />
          <Select
            label="Category"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            options={categoryOptions}
          />
        </div>
      </div>

      {/* Category Stats */}
      {categoryStats.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Expenses by Category</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {categoryStats.map((stat) => (
              <div key={stat.category} className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-600 capitalize">{stat.category}</p>
                <p className="text-xl font-bold text-gray-900 mt-1">${stat.total.toFixed(2)}</p>
                <p className="text-xs text-gray-500 mt-1">{stat.count} items</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expenses Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Receipt
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {expenses.map((expense) => (
                <tr key={expense.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {new Date(expense.expense_date).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                      {expense.category || 'Other'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{expense.description}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="text-sm font-medium text-gray-900">${expense.amount.toFixed(2)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    {expense.receipt_url ? (
                      <a
                        href={expense.receipt_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View
                      </a>
                    ) : (
                      <span className="text-gray-400">No receipt</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button
                      onClick={() => handleDeleteExpense(expense.id)}
                      disabled={actionLoading === expense.id}
                      className="text-red-600 hover:text-red-900 disabled:opacity-50"
                      title="Delete"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {expenses.length === 0 && (
          <EmptyState
            icon={DollarSign}
            title="No Expenses Found"
            description="No expenses recorded for the selected period"
            action={{
              label: 'Add Expense',
              onClick: () => setShowAddModal(true),
            }}
          />
        )}
      </div>

      {/* Add Expense Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Add New Expense</h2>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <Input
                label="Amount"
                type="number"
                step="0.01"
                min="0"
                value={formData.amount || ''}
                onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                placeholder="Enter amount"
                required
                leftIcon={<DollarSign className="w-5 h-5" />}
              />

              <Input
                label="Date"
                type="date"
                value={formData.expense_date}
                onChange={(e) => {
                  const date = e.target.value;
                  const month = date.slice(0, 7);
                  setFormData({ ...formData, expense_date: date, month });
                }}
                required
                leftIcon={<Calendar className="w-5 h-5" />}
              />

              <Select
                label="Category"
                value={formData.category}
                onChange={(e) =>
                  setFormData({ ...formData, category: e.target.value as ExpenseCategory })
                }
                options={categoryOptions.filter((o) => o.value !== 'all')}
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Enter expense description"
                  rows={3}
                  className="block w-full px-4 py-2.5 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Receipt (optional)
                </label>
                <div className="flex items-center gap-2">
                  <label className="flex-1 flex items-center justify-center px-4 py-2.5 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                    <Upload className="w-5 h-5 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-600">
                      {receiptFile ? receiptFile.name : 'Upload receipt'}
                    </span>
                    <input
                      type="file"
                      accept="image/*,.pdf"
                      onChange={(e) => setReceiptFile(e.target.files?.[0] || null)}
                      className="hidden"
                    />
                  </label>
                  {receiptFile && (
                    <button
                      onClick={() => setReceiptFile(null)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAddModal(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleAddExpense} disabled={actionLoading === 'add'}>
                {actionLoading === 'add' ? 'Adding...' : 'Add Expense'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Expenses;
