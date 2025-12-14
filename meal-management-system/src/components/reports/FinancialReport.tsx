import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { Download, FileText, Table, Loader2, Calendar } from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  generateFinancialReportPDF,
  exportFinancialReportExcel
} from '../../services/reports.service';
import {
  getDepositsByDateRange,
  getTotalDepositsByMonth
} from '../../services/deposits.service';
import {
  getExpensesByDateRange,
  getTotalExpensesByMonth
} from '../../services/expenses.service';

interface FinancialReportProps {
  initialMonth?: string;
}

export const FinancialReport: React.FC<FinancialReportProps> = ({ initialMonth }) => {
  const [selectedMonth, setSelectedMonth] = useState<string>(
    initialMonth || format(new Date(), 'yyyy-MM')
  );
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [useCustomRange, setUseCustomRange] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [summary, setSummary] = useState({
    totalDeposits: 0,
    totalExpenses: 0,
    balance: 0,
    depositsCount: 0,
    expensesCount: 0
  });

  // Calculate date range based on selected month or custom dates
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
      const [depositsResponse, expensesResponse] = await Promise.all([
        getDepositsByDateRange(startDate, endDate),
        getExpensesByDateRange(startDate, endDate)
      ]);

      if (depositsResponse.success && expensesResponse.success) {
        const deposits = depositsResponse.data || [];
        const expenses = expensesResponse.data || [];

        const totalDeposits = deposits.reduce((sum, d) => sum + d.amount, 0);
        const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);

        setSummary({
          totalDeposits,
          totalExpenses,
          balance: totalDeposits - totalExpenses,
          depositsCount: deposits.length,
          expensesCount: expenses.length
        });
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
      toast.error('Failed to fetch financial summary');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    setGenerating(true);
    try {
      await generateFinancialReportPDF(
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
      await exportFinancialReportExcel(
        startDate,
        endDate,
        useCustomRange ? undefined : selectedMonth
      );
      toast.success('Excel file exported successfully!');
    } catch (error) {
      console.error('Error exporting Excel:', error);
      toast.error('Failed to export Excel file');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Financial Report
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            View and export comprehensive financial reports
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

      {/* Summary Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Total Deposits Card */}
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                  Total Deposits
                </p>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-2">
                  Rs. {summary.totalDeposits.toFixed(2)}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  {summary.depositsCount} transactions
                </p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Download className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          {/* Total Expenses Card */}
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                  Total Expenses
                </p>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-2">
                  Rs. {summary.totalExpenses.toFixed(2)}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  {summary.expensesCount} transactions
                </p>
              </div>
              <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
                <Download className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </div>

          {/* Balance Card */}
          <div className={`bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6 border-l-4 ${
            summary.balance >= 0 ? 'border-blue-500' : 'border-orange-500'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                  Balance
                </p>
                <p className={`text-2xl font-bold mt-2 ${
                  summary.balance >= 0
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-orange-600 dark:text-orange-400'
                }`}>
                  Rs. {summary.balance.toFixed(2)}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  {summary.balance >= 0 ? 'Surplus' : 'Deficit'}
                </p>
              </div>
              <div className={`p-3 rounded-lg ${
                summary.balance >= 0
                  ? 'bg-blue-100 dark:bg-blue-900/30'
                  : 'bg-orange-100 dark:bg-orange-900/30'
              }`}>
                <Calendar className={`w-6 h-6 ${
                  summary.balance >= 0
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-orange-600 dark:text-orange-400'
                }`} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info Section */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex gap-3">
          <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800 dark:text-blue-300">
            <p className="font-medium mb-1">About Financial Reports</p>
            <p>
              Financial reports include detailed information about all deposits and expenses
              for the selected period. PDF reports are formatted for printing, while Excel
              exports allow for further analysis and custom calculations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialReport;
