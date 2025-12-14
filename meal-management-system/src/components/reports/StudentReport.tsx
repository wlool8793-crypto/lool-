import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { FileText, Table, Loader2, User, Search } from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  generateStudentReportPDF,
  exportToExcel
} from '../../services/reports.service';
import { getAllUsers, getUserById } from '../../services/users.service';
import { getDepositsByDateRange } from '../../services/deposits.service';
import { getMealsByDateRange } from '../../services/meals.service';
import { User as UserType } from '../../types/database.types';

interface StudentReportProps {
  initialMonth?: string;
  initialUserId?: string;
}

export const StudentReport: React.FC<StudentReportProps> = ({
  initialMonth,
  initialUserId
}) => {
  const [selectedMonth, setSelectedMonth] = useState<string>(
    initialMonth || format(new Date(), 'yyyy-MM')
  );
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [useCustomRange, setUseCustomRange] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string>(initialUserId || '');
  const [users, setUsers] = useState<UserType[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [summary, setSummary] = useState({
    userName: '',
    email: '',
    roomNumber: '',
    totalDeposits: 0,
    totalMeals: 0,
    breakfastCount: 0,
    lunchCount: 0,
    dinnerCount: 0,
    depositsCount: 0
  });

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

  // Fetch users
  useEffect(() => {
    fetchUsers();
  }, []);

  // Fetch summary when user or dates change
  useEffect(() => {
    if (selectedUserId && startDate && endDate) {
      fetchSummary();
    }
  }, [selectedUserId, startDate, endDate]);

  const fetchUsers = async () => {
    try {
      const response = await getAllUsers();
      if (response.success) {
        const studentUsers = (response.data || []).filter(u => u.role === 'student' && u.is_active);
        setUsers(studentUsers);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      toast.error('Failed to fetch users');
    }
  };

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const [userResponse, depositsResponse, mealsResponse] = await Promise.all([
        getUserById(selectedUserId),
        getDepositsByDateRange(startDate, endDate),
        getMealsByDateRange(startDate, endDate)
      ]);

      if (userResponse.success && depositsResponse.success && mealsResponse.success) {
        const user = userResponse.data;
        const allDeposits = depositsResponse.data || [];
        const allMeals = mealsResponse.data || [];

        // Filter user-specific data
        const userDeposits = allDeposits.filter(d => d.user_id === selectedUserId);
        const userMeals = allMeals.filter(m => m.user_id === selectedUserId);

        const totalDeposits = userDeposits.reduce((sum, d) => sum + d.amount, 0);

        let breakfastCount = 0;
        let lunchCount = 0;
        let dinnerCount = 0;

        userMeals.forEach(meal => {
          if (meal.breakfast) breakfastCount++;
          if (meal.lunch) lunchCount++;
          if (meal.dinner) dinnerCount++;
        });

        setSummary({
          userName: user?.full_name || '',
          email: user?.email || '',
          roomNumber: user?.room_number || 'N/A',
          totalDeposits,
          totalMeals: breakfastCount + lunchCount + dinnerCount,
          breakfastCount,
          lunchCount,
          dinnerCount,
          depositsCount: userDeposits.length
        });
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
      toast.error('Failed to fetch student summary');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    if (!selectedUserId) {
      toast.error('Please select a student');
      return;
    }

    setGenerating(true);
    try {
      await generateStudentReportPDF(
        selectedUserId,
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
    if (!selectedUserId) {
      toast.error('Please select a student');
      return;
    }

    setGenerating(true);
    try {
      const [depositsResponse, mealsResponse] = await Promise.all([
        getDepositsByDateRange(startDate, endDate),
        getMealsByDateRange(startDate, endDate)
      ]);

      if (depositsResponse.success && mealsResponse.success) {
        const allDeposits = depositsResponse.data || [];
        const allMeals = mealsResponse.data || [];

        const userDeposits = allDeposits.filter(d => d.user_id === selectedUserId);
        const userMeals = allMeals.filter(m => m.user_id === selectedUserId);

        const depositsData = userDeposits.map(d => ({
          Date: format(new Date(d.deposit_date), 'yyyy-MM-dd'),
          Amount: d.amount,
          'Payment Method': d.payment_method || 'N/A',
          Notes: d.notes || '-'
        }));

        const mealsData = userMeals.map(m => ({
          Date: format(new Date(m.meal_date), 'yyyy-MM-dd'),
          Breakfast: m.breakfast ? 'Yes' : 'No',
          Lunch: m.lunch ? 'Yes' : 'No',
          Dinner: m.dinner ? 'Yes' : 'No'
        }));

        // Export using multi-sheet function
        const { exportMultiSheetExcel } = await import('../../services/reports.service');
        await exportMultiSheetExcel(
          [
            { data: depositsData, sheetName: 'Deposits' },
            { data: mealsData, sheetName: 'Meals' }
          ],
          `student-report-${summary.userName.replace(/\s+/g, '-').toLowerCase()}-${
            useCustomRange ? 'custom' : selectedMonth
          }`
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

  const filteredUsers = users.filter(
    user =>
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (user.room_number && user.room_number.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Student Report
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Individual student activity and financial summary
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleGeneratePDF}
            disabled={generating || loading || !selectedUserId}
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
            disabled={generating || loading || !selectedUserId}
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

      {/* Student Selection */}
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          Select Student
        </h3>
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by name, email, or room..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
            />
          </div>
          <select
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
          >
            <option value="">Select a student...</option>
            {filteredUsers.map(user => (
              <option key={user.id} value={user.id}>
                {user.full_name} - {user.email} {user.room_number ? `(Room ${user.room_number})` : ''}
              </option>
            ))}
          </select>
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

      {/* Summary */}
      {selectedUserId && (
        loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : (
          <>
            {/* Student Info */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg shadow-lg p-6 text-white">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-white/20 rounded-full">
                  <User className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">{summary.userName}</h3>
                  <p className="text-white/90">{summary.email}</p>
                  <p className="text-white/80 text-sm mt-1">Room: {summary.roomNumber}</p>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Financial Summary */}
              <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                  Financial Summary
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 dark:text-slate-400">Total Deposits</span>
                    <span className="text-xl font-bold text-green-600 dark:text-green-400">
                      Rs. {summary.totalDeposits.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 dark:text-slate-400">Transactions</span>
                    <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                      {summary.depositsCount}
                    </span>
                  </div>
                </div>
              </div>

              {/* Meal Summary */}
              <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                  Meal Summary
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 dark:text-slate-400">Total Meals</span>
                    <span className="text-xl font-bold text-blue-600 dark:text-blue-400">
                      {summary.totalMeals}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mt-3">
                    <div className="text-center p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                      <p className="text-xs text-slate-600 dark:text-slate-400">Breakfast</p>
                      <p className="text-lg font-semibold text-yellow-900 dark:text-yellow-200">
                        {summary.breakfastCount}
                      </p>
                    </div>
                    <div className="text-center p-2 bg-orange-50 dark:bg-orange-900/20 rounded">
                      <p className="text-xs text-slate-600 dark:text-slate-400">Lunch</p>
                      <p className="text-lg font-semibold text-orange-900 dark:text-orange-200">
                        {summary.lunchCount}
                      </p>
                    </div>
                    <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
                      <p className="text-xs text-slate-600 dark:text-slate-400">Dinner</p>
                      <p className="text-lg font-semibold text-purple-900 dark:text-purple-200">
                        {summary.dinnerCount}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )
      )}

      {/* Info Section */}
      {!selectedUserId && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex gap-3">
            <User className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800 dark:text-blue-300">
              <p className="font-medium mb-1">Select a Student</p>
              <p>
                Choose a student from the dropdown above to view their detailed report including
                deposits, meal consumption, and activity summary.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentReport;
