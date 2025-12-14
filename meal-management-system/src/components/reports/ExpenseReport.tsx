import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { FileText, Table, Loader2, TrendingUp } from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  generateExpenseReportPDF,
  exportToExcel
} from '../../services/reports.service';
import { getExpensesByDateRange } from '../../services/expenses.service';
import { ExpenseCategory } from '../../types/database.types';

interface ExpenseReportProps {
  initialMonth?: string;
}

export const ExpenseReport: React.FC<ExpenseReportProps> = ({ initialMonth }) => {
  const [selectedMonth, setSelectedMonth] = useState<string>(
    initialMonth || format(new Date(), 'yyyy-MM')
  );
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [useCustomRange, setUseCustomRange] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [categoryBreakdown, setCategoryBreakdown] = useState<
    { category: string; amount: number; percentage: number; count: number }[]
  >([]);
  const [totalExpenses, setTotalExpenses] = useState(0);

  // Calculate date range
  useEffect(() => {
    if (!useCustomRange && selectedMonth) {
      const monthDate = new Date(selectedMonth + '-01');
      const start = format(startOfMonth(monthDate), 'yyyy-MM-dd');
      const end = format(endOfMonth(monthDate), 'yyyy-MM-dd');
      setStartDate(start);
      setEndDate(end);
    }
  }, [selectedMonth, useCustomRange]);

  // Fetch summary data
  useEffect(() => {
    if (startDate && endDate) {
      fetchSummary();
    }
  }, [startDate, endDate]);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const expensesResponse = await getExpensesByDateRange(startDate, endDate);

      if (expensesResponse.success) {
        const expenses = expensesResponse.data || [];
        const total = expenses.reduce((sum, e) => sum + e.amount, 0);
        setTotalExpenses(total);

        // Calculate category breakdown
        const categoryMap = new Map<string, { amount: number; count: number }>();
        expenses.forEach(expense => {
          const category = expense.category || 'other';
          const current = categoryMap.get(category) || { amount: 0, count: 0 };
          categoryMap.set(category, {
            amount: current.amount + expense.amount,
            count: current.count + 1
          });
        });

        const breakdown = Array.from(categoryMap.entries()).map(([category, data]) => ({
          category: category.charAt(0).toUpperCase() + category.slice(1),
          amount: data.amount,
          percentage: total > 0 ? (data.amount / total) * 100 : 0,
          count: data.count
        }));

        // Sort by amount descending
        breakdown.sort((a, b) => b.amount - a.amount);
        setCategoryBreakdown(breakdown);
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
      toast.error('Failed to fetch expense summary');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    setGenerating(true);
    try {
      await generateExpenseReportPDF(
        startDate,
        endDate,
        useCustomRange ? undefined : selectedMonth
      );
      toast.success('PDF report generated successfully!');
    } catch (error) {
      console.error('Error generating PDF:', error);
      toast.error('Failed to generate PDF report');
    } finally {
      setGenerating(false);
    }
  };

  const handleExportExcel = async () => {
    setGenerating(true);
    try {
      const expensesResponse = await getExpensesByDateRange(startDate, endDate);
      if (expensesResponse.success) {
        const expenses = expensesResponse.data || [];
        const excelData = expenses.map(e => ({
          Date: format(new Date(e.expense_date), 'yyyy-MM-dd'),
          Category: (e.category || 'other').charAt(0).toUpperCase() + (e.category || 'other').slice(1),
          Amount: e.amount,
          Description: e.description
        }));

        await exportToExcel(
          excelData,
          'Expenses',
          `expense-report-${useCustomRange ? 'custom' : selectedMonth}`
        );
        toast.success('Excel file exported successfully!');
      }
    } catch (error) {
      console.error('Error exporting Excel:', error);
      toast.error('Failed to export Excel file');
    } finally {
      setGenerating(false);
    }
  };

  const getCategoryColor = (index: number) => {
    const colors = [
      'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-300',
      'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800 text-orange-800 dark:text-orange-300',
      'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-300',
      'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-300',
      'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300',
      'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800 text-purple-800 dark:text-purple-300',
      'bg-pink-50 dark:bg-pink-900/20 border-pink-200 dark:border-pink-800 text-pink-800 dark:text-pink-300'
    ];
    return colors[index % colors.length];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Expense Analysis Report
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Analyze expense patterns and category-wise breakdown
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleGeneratePDF}
            disabled={generating || loading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileText className="w-4 h-4" />
            )}
            Export PDF
          </button>
          <button
            onClick={handleExportExcel}
            disabled={generating || loading}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Table className="w-4 h-4" />
            )}
            Export Excel
          </button>
        </div>
      </div>

      {/* Date Selection */}
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          Select Period
        </h3>
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useCustomRange"
              checked={useCustomRange}
              onChange={(e) => setUseCustomRange(e.target.checked)}
              className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            <label
              htmlFor="useCustomRange"
              className="text-sm text-slate-700 dark:text-slate-300"
            >
              Use custom date range
            </label>
          </div>

          {useCustomRange ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
                />
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Select Month
              </label>
              <input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="w-full sm:w-64 px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
              />
            </div>
          )}
        </div>
      </div>

      {/* Total Expenses Card */}
      <div className="bg-gradient-to-r from-red-500 to-orange-500 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/90 text-sm font-medium">Total Expenses</p>
            <p className="text-4xl font-bold mt-2">Rs. {totalExpenses.toFixed(2)}</p>
            <p className="text-white/80 text-sm mt-1">
              {categoryBreakdown.reduce((sum, cat) => sum + cat.count, 0)} transactions
            </p>
          </div>
          <div className="p-4 bg-white/20 rounded-lg">
            <TrendingUp className="w-8 h-8" />
          </div>
        </div>
      </div>

      {/* Category Breakdown */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
            Category Breakdown
          </h3>
          {categoryBreakdown.length === 0 ? (
            <p className="text-slate-500 dark:text-slate-400 text-center py-8">
              No expenses found for the selected period
            </p>
          ) : (
            <div className="space-y-4">
              {categoryBreakdown.map((item, index) => (
                <div key={item.category} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(index)}`}>
                        {item.category}
                      </div>
                      <span className="text-sm text-slate-600 dark:text-slate-400">
                        {item.count} {item.count === 1 ? 'transaction' : 'transactions'}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                        Rs. {item.amount.toFixed(2)}
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {item.percentage.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full transition-all"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Info Section */}
      <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
        <div className="flex gap-3">
          <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-purple-800 dark:text-purple-300">
            <p className="font-medium mb-1">About Expense Reports</p>
            <p>
              Expense reports provide detailed analysis of spending patterns across different
              categories. Use these insights to identify cost-saving opportunities and optimize
              budget allocation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpenseReport;
