import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Wallet,
  Calendar,
  TrendingUp,
  Coffee,
  UtensilsCrossed,
  Moon,
  AlertCircle,
  ArrowRight,
  Loader2,
  DollarSign,
  Users,
  Bell,
} from 'lucide-react';
import { getCurrentUser } from '../../services/auth.service';
import { getMealsByUser, getMealStatsByUserAndMonth } from '../../services/meals.service';
import { getDepositsByUser, getTotalDepositsByUserAndMonth } from '../../services/deposits.service';
import { User, Meal, Deposit } from '../../types/database.types';
import toast from 'react-hot-toast';
import { format, startOfMonth, endOfMonth } from 'date-fns';

interface DashboardStats {
  balance: number;
  totalDeposits: number;
  totalMeals: number;
  totalBreakfast: number;
  totalLunch: number;
  totalDinner: number;
  guestMeals: number;
}

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<DashboardStats>({
    balance: 0,
    totalDeposits: 0,
    totalMeals: 0,
    totalBreakfast: 0,
    totalLunch: 0,
    totalDinner: 0,
    guestMeals: 0,
  });
  const [recentMeals, setRecentMeals] = useState<Meal[]>([]);
  const [recentDeposits, setRecentDeposits] = useState<Deposit[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentMonth] = useState(format(new Date(), 'yyyy-MM'));

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);

    try {
      // Get current user
      const userResult = await getCurrentUser();
      if (userResult.success && userResult.data) {
        setUser(userResult.data);
        await loadUserStats(userResult.data.id);
      } else {
        toast.error('Failed to load user data');
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserStats = async (userId: string) => {
    try {
      // Get meal statistics for current month
      const mealStatsResult = await getMealStatsByUserAndMonth(userId, currentMonth);

      // Get total deposits for current month
      const depositsResult = await getTotalDepositsByUserAndMonth(userId, currentMonth);

      // Get recent meals (last 5)
      const startDate = format(startOfMonth(new Date()), 'yyyy-MM-dd');
      const endDate = format(endOfMonth(new Date()), 'yyyy-MM-dd');
      const mealsResult = await getMealsByUser(userId, startDate, endDate);

      // Get recent deposits (last 3)
      const allDepositsResult = await getDepositsByUser(userId);

      if (mealStatsResult.success && mealStatsResult.data) {
        const mealData = mealStatsResult.data;
        const totalMeals =
          mealData.total_breakfast + mealData.total_lunch + mealData.total_dinner;
        const guestMeals =
          mealData.total_guest_breakfast +
          mealData.total_guest_lunch +
          mealData.total_guest_dinner;

        // Calculate approximate balance (deposits - estimated meal costs)
        const totalDeposits = depositsResult.success ? depositsResult.data || 0 : 0;
        const estimatedMealCost = totalMeals * 60; // Assuming 60 per meal
        const estimatedGuestCost = guestMeals * 70; // Assuming 70 per guest meal
        const balance = totalDeposits - estimatedMealCost - estimatedGuestCost;

        setStats({
          balance,
          totalDeposits,
          totalMeals,
          totalBreakfast: mealData.total_breakfast,
          totalLunch: mealData.total_lunch,
          totalDinner: mealData.total_dinner,
          guestMeals,
        });
      }

      if (mealsResult.success && mealsResult.data) {
        setRecentMeals(mealsResult.data.slice(0, 5));
      }

      if (allDepositsResult.success && allDepositsResult.data) {
        setRecentDeposits(allDepositsResult.data.slice(0, 3));
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600 dark:text-indigo-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow dark:shadow-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Welcome back, {user?.full_name || 'Student'}!
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Here's your meal management overview for {format(new Date(), 'MMMM yyyy')}
              </p>
            </div>
            <Link
              to="/student/profile"
              className="flex items-center px-4 py-2 bg-indigo-600 dark:bg-indigo-500 text-white rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors"
            >
              <Users className="w-5 h-5 mr-2" />
              View Profile
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Balance Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700/50 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Current Balance</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  Rs. {stats.balance.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Wallet className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
            <div className="mt-4">
              <Link
                to="/student/financial-summary"
                className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium flex items-center"
              >
                View Details
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>

          {/* Total Deposits Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700/50 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Deposits</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  Rs. {stats.totalDeposits.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">This month</p>
          </div>

          {/* Total Meals Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700/50 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Meals</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{stats.totalMeals}</p>
              </div>
              <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <UtensilsCrossed className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
              B: {stats.totalBreakfast} | L: {stats.totalLunch} | D: {stats.totalDinner}
            </p>
          </div>

          {/* Guest Meals Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700/50 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Guest Meals</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{stats.guestMeals}</p>
              </div>
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Users className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">This month</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700/50 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              to="/student/meal-planner"
              className="flex items-center p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-indigo-500 dark:hover:border-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all group"
            >
              <Calendar className="w-8 h-8 text-indigo-600 dark:text-indigo-400 mr-3" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white group-hover:text-indigo-700 dark:group-hover:text-indigo-300">
                  Plan Meals
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Manage monthly meals</p>
              </div>
            </Link>

            <Link
              to="/student/financial-summary"
              className="flex items-center p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-green-500 dark:hover:border-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all group"
            >
              <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400 mr-3" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white group-hover:text-green-700 dark:group-hover:text-green-300">
                  View Finances
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Deposits & expenses</p>
              </div>
            </Link>

            <Link
              to="/student/profile"
              className="flex items-center p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all group"
            >
              <Users className="w-8 h-8 text-blue-600 dark:text-blue-400 mr-3" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white group-hover:text-blue-700 dark:group-hover:text-blue-300">
                  My Profile
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Update information</p>
              </div>
            </Link>

            <Link
              to="/student/notifications"
              className="flex items-center p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-yellow-500 dark:hover:border-yellow-400 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-all group"
            >
              <Bell className="w-8 h-8 text-yellow-600 dark:text-yellow-400 mr-3" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white group-hover:text-yellow-700 dark:group-hover:text-yellow-300">
                  Notifications
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">View updates</p>
              </div>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Meals */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700/50">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Meals</h2>
                <Link
                  to="/student/meal-planner"
                  className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium"
                >
                  View All
                </Link>
              </div>
            </div>
            <div className="p-6">
              {recentMeals.length === 0 ? (
                <div className="text-center py-8">
                  <UtensilsCrossed className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-500 dark:text-gray-400">No meals planned yet</p>
                  <Link
                    to="/student/meal-planner"
                    className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium mt-2 inline-block"
                  >
                    Plan your first meal
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentMeals.map((meal) => (
                    <div
                      key={meal.id}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {format(new Date(meal.meal_date), 'MMM dd, yyyy')}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          {meal.breakfast && (
                            <span className="flex items-center text-xs text-gray-600 dark:text-gray-400">
                              <Coffee className="w-3 h-3 mr-1" />
                              Breakfast
                            </span>
                          )}
                          {meal.lunch && (
                            <span className="flex items-center text-xs text-gray-600 dark:text-gray-400">
                              <UtensilsCrossed className="w-3 h-3 mr-1" />
                              Lunch
                            </span>
                          )}
                          {meal.dinner && (
                            <span className="flex items-center text-xs text-gray-600 dark:text-gray-400">
                              <Moon className="w-3 h-3 mr-1" />
                              Dinner
                            </span>
                          )}
                        </div>
                      </div>
                      {(meal.guest_breakfast > 0 ||
                        meal.guest_lunch > 0 ||
                        meal.guest_dinner > 0) && (
                        <div className="text-xs text-purple-600 dark:text-purple-400 font-medium">
                          +{meal.guest_breakfast + meal.guest_lunch + meal.guest_dinner} guests
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Deposits */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700/50">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Deposits</h2>
                <Link
                  to="/student/financial-summary"
                  className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium"
                >
                  View All
                </Link>
              </div>
            </div>
            <div className="p-6">
              {recentDeposits.length === 0 ? (
                <div className="text-center py-8">
                  <Wallet className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-500 dark:text-gray-400">No deposits yet</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    Contact your hostel manager to add deposits
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentDeposits.map((deposit) => (
                    <div
                      key={deposit.id}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          Rs. {deposit.amount.toFixed(2)}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {format(new Date(deposit.deposit_date), 'MMM dd, yyyy')}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                          {deposit.payment_method || 'cash'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Important Notice */}
        <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-300">Important Reminder</h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-400 mt-1">
                Remember to plan your meals before the deadline. Late cancellations may incur
                penalty charges. Check the meal planner for specific deadlines.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
