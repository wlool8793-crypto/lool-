import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Calendar,
  DollarSign,
  FileText,
  Download,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';
import { getCurrentUser } from '../../services/auth.service';
import { getDepositsByUser } from '../../services/deposits.service';
import { getMealsByUser } from '../../services/meals.service';
import { User, Deposit, Meal } from '../../types/database.types';
import toast from 'react-hot-toast';
import { format, startOfMonth, endOfMonth, subMonths, addMonths } from 'date-fns';

interface MonthlyFinancials {
  month: string;
  totalDeposits: number;
  totalMealCost: number;
  totalGuestMealCost: number;
  balance: number;
  deposits: Deposit[];
  meals: Meal[];
}

const FinancialSummary: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [monthlyData, setMonthlyData] = useState<MonthlyFinancials | null>(null);
  const [allDeposits, setAllDeposits] = useState<Deposit[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState<'all' | 'deposits' | 'expenses'>('all');

  // Pricing constants (should ideally come from settings)
  const MEAL_PRICE = 60;
  const GUEST_MEAL_PRICE = 70;

  useEffect(() => {
    loadUserData();
  }, []);

  useEffect(() => {
    if (user) {
      loadMonthlyFinancials();
    }
  }, [user, currentDate]);

  const loadUserData = async () => {
    try {
      const userResult = await getCurrentUser();
      if (!userResult.success || !userResult.data) {
        toast.error('Failed to load user data');
        navigate('/login');
        return;
      }

      setUser(userResult.data);
    } catch (error) {
      console.error('Error loading user:', error);
      toast.error('Failed to load user data');
    }
  };

  const loadMonthlyFinancials = async () => {
    if (!user) return;

    setIsLoading(true);

    try {
      const monthStr = format(currentDate, 'yyyy-MM');
      const startDate = format(startOfMonth(currentDate), 'yyyy-MM-dd');
      const endDate = format(endOfMonth(currentDate), 'yyyy-MM-dd');

      // Load deposits
      const depositsResult = await getDepositsByUser(user.id);
      if (depositsResult.success && depositsResult.data) {
        setAllDeposits(depositsResult.data);

        const monthDeposits = depositsResult.data.filter(
          (d) => d.month === monthStr || format(new Date(d.deposit_date), 'yyyy-MM') === monthStr
        );

        // Load meals
        const mealsResult = await getMealsByUser(user.id, startDate, endDate);
        const meals = mealsResult.success ? mealsResult.data || [] : [];

        // Calculate totals
        const totalDeposits = monthDeposits.reduce((sum, d) => sum + d.amount, 0);

        let totalMealCount = 0;
        let totalGuestMealCount = 0;

        meals.forEach((meal) => {
          if (meal.breakfast) totalMealCount++;
          if (meal.lunch) totalMealCount++;
          if (meal.dinner) totalMealCount++;

          totalGuestMealCount +=
            meal.guest_breakfast + meal.guest_lunch + meal.guest_dinner;
        });

        const totalMealCost = totalMealCount * MEAL_PRICE;
        const totalGuestMealCost = totalGuestMealCount * GUEST_MEAL_PRICE;
        const balance = totalDeposits - totalMealCost - totalGuestMealCost;

        setMonthlyData({
          month: monthStr,
          totalDeposits,
          totalMealCost,
          totalGuestMealCost,
          balance,
          deposits: monthDeposits,
          meals,
        });
      }
    } catch (error) {
      console.error('Error loading financials:', error);
      toast.error('Failed to load financial data');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreviousMonth = () => {
    setCurrentDate(subMonths(currentDate, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(addMonths(currentDate, 1));
  };

  const handleDownloadReport = () => {
    if (!monthlyData) return;

    // Create CSV content
    let csvContent = 'Financial Summary Report\n';
    csvContent += `Month: ${format(currentDate, 'MMMM yyyy')}\n`;
    csvContent += `Student: ${user?.full_name}\n\n`;

    csvContent += 'Summary\n';
    csvContent += `Total Deposits,Rs. ${monthlyData.totalDeposits.toFixed(2)}\n`;
    csvContent += `Total Meal Cost,Rs. ${monthlyData.totalMealCost.toFixed(2)}\n`;
    csvContent += `Total Guest Meal Cost,Rs. ${monthlyData.totalGuestMealCost.toFixed(2)}\n`;
    csvContent += `Balance,Rs. ${monthlyData.balance.toFixed(2)}\n\n`;

    csvContent += 'Deposits\n';
    csvContent += 'Date,Amount,Payment Method,Notes\n';
    monthlyData.deposits.forEach((deposit) => {
      csvContent += `${format(new Date(deposit.deposit_date), 'yyyy-MM-dd')},${
        deposit.amount
      },${deposit.payment_method || 'cash'},"${deposit.notes || ''}"\n`;
    });

    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute(
      'download',
      `financial_summary_${format(currentDate, 'yyyy-MM')}.csv`
    );
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast.success('Report downloaded successfully');
  };

  const getFilteredTransactions = () => {
    if (!monthlyData) return [];

    const transactions: Array<{
      id: string;
      type: 'deposit' | 'expense';
      date: string;
      amount: number;
      description: string;
      paymentMethod?: string;
    }> = [];

    if (filterType === 'all' || filterType === 'deposits') {
      monthlyData.deposits.forEach((deposit) => {
        transactions.push({
          id: deposit.id,
          type: 'deposit',
          date: deposit.deposit_date,
          amount: deposit.amount,
          description: deposit.notes || 'Deposit',
          paymentMethod: deposit.payment_method,
        });
      });
    }

    if (filterType === 'all' || filterType === 'expenses') {
      monthlyData.meals.forEach((meal) => {
        const mealTypes: string[] = [];
        let mealCost = 0;

        if (meal.breakfast) {
          mealTypes.push('Breakfast');
          mealCost += MEAL_PRICE;
        }
        if (meal.lunch) {
          mealTypes.push('Lunch');
          mealCost += MEAL_PRICE;
        }
        if (meal.dinner) {
          mealTypes.push('Dinner');
          mealCost += MEAL_PRICE;
        }

        const guestCount =
          meal.guest_breakfast + meal.guest_lunch + meal.guest_dinner;
        if (guestCount > 0) {
          mealCost += guestCount * GUEST_MEAL_PRICE;
          mealTypes.push(`${guestCount} guest(s)`);
        }

        if (mealTypes.length > 0) {
          transactions.push({
            id: meal.id,
            type: 'expense',
            date: meal.meal_date,
            amount: mealCost,
            description: mealTypes.join(', '),
          });
        }
      });
    }

    return transactions.sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading financial summary...</p>
        </div>
      </div>
    );
  }

  const transactions = getFilteredTransactions();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <Wallet className="w-7 h-7 mr-3 text-indigo-600" />
                Financial Summary
              </h1>
              <p className="text-gray-600 mt-1">View your deposits and expenses</p>
            </div>
            <button
              onClick={handleDownloadReport}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Download className="w-5 h-5 mr-2" />
              Download Report
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Month Navigation */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <button
              onClick={handlePreviousMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-6 h-6 text-gray-600" />
            </button>
            <h2 className="text-xl font-semibold text-gray-900">
              {format(currentDate, 'MMMM yyyy')}
            </h2>
            <button
              onClick={handleNextMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        {monthlyData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Total Deposits */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
              </div>
              <p className="text-sm font-medium text-gray-600">Total Deposits</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                Rs. {monthlyData.totalDeposits.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {monthlyData.deposits.length} transaction(s)
              </p>
            </div>

            {/* Meal Expenses */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-red-100 rounded-lg">
                  <TrendingDown className="w-6 h-6 text-red-600" />
                </div>
              </div>
              <p className="text-sm font-medium text-gray-600">Meal Expenses</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                Rs. {monthlyData.totalMealCost.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-2">Regular meals</p>
            </div>

            {/* Guest Meal Expenses */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <TrendingDown className="w-6 h-6 text-purple-600" />
                </div>
              </div>
              <p className="text-sm font-medium text-gray-600">Guest Meals</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                Rs. {monthlyData.totalGuestMealCost.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-2">Additional charges</p>
            </div>

            {/* Balance */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div
                  className={`p-3 rounded-lg ${
                    monthlyData.balance >= 0 ? 'bg-blue-100' : 'bg-orange-100'
                  }`}
                >
                  <DollarSign
                    className={`w-6 h-6 ${
                      monthlyData.balance >= 0 ? 'text-blue-600' : 'text-orange-600'
                    }`}
                  />
                </div>
              </div>
              <p className="text-sm font-medium text-gray-600">Current Balance</p>
              <p
                className={`text-2xl font-bold mt-2 ${
                  monthlyData.balance >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                Rs. {monthlyData.balance.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {monthlyData.balance >= 0 ? 'Available' : 'Outstanding'}
              </p>
            </div>
          </div>
        )}

        {/* Transaction History */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <h2 className="text-lg font-semibold text-gray-900">Transaction History</h2>

              {/* Filter Buttons */}
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <button
                  onClick={() => setFilterType('all')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    filterType === 'all'
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setFilterType('deposits')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    filterType === 'deposits'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Deposits
                </button>
                <button
                  onClick={() => setFilterType('expenses')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    filterType === 'expenses'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Expenses
                </button>
              </div>
            </div>
          </div>

          <div className="p-6">
            {transactions.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No transactions found for this period</p>
              </div>
            ) : (
              <div className="space-y-3">
                {transactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center flex-1">
                      <div
                        className={`p-2 rounded-lg mr-4 ${
                          transaction.type === 'deposit'
                            ? 'bg-green-100'
                            : 'bg-red-100'
                        }`}
                      >
                        {transaction.type === 'deposit' ? (
                          <TrendingUp className="w-5 h-5 text-green-600" />
                        ) : (
                          <TrendingDown className="w-5 h-5 text-red-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">
                          {transaction.description}
                        </p>
                        <div className="flex items-center gap-3 mt-1">
                          <p className="text-sm text-gray-500 flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {format(new Date(transaction.date), 'MMM dd, yyyy')}
                          </p>
                          {transaction.paymentMethod && (
                            <span className="text-xs px-2 py-1 bg-gray-200 text-gray-700 rounded">
                              {transaction.paymentMethod}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <p
                        className={`text-lg font-semibold ${
                          transaction.type === 'deposit'
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {transaction.type === 'deposit' ? '+' : '-'}Rs.{' '}
                        {transaction.amount.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Pricing Info */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Pricing Information</h3>
          <div className="text-sm text-blue-700 space-y-1">
            <p>Regular Meal: Rs. {MEAL_PRICE} per meal</p>
            <p>Guest Meal: Rs. {GUEST_MEAL_PRICE} per meal</p>
            <p className="text-xs text-blue-600 mt-2">
              * Prices may vary based on monthly settings
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialSummary;
