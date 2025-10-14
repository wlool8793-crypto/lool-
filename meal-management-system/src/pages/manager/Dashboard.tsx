import React, { useState, useEffect } from 'react';
import {
  Users,
  Coffee,
  UtensilsCrossed,
  Moon,
  TrendingUp,
  AlertCircle,
  Download,
  RefreshCw,
  DollarSign,
  Clock
} from 'lucide-react';
import { StatCard } from '../../components/dashboard/StatCard';
import { Button } from '../../components/forms/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { getMealsByDate } from '../../services/meals.service';
import { getAllUsers } from '../../services/users.service';
import { getTotalExpensesByMonth } from '../../services/expenses.service';
import { getDepositsByMonth } from '../../services/deposits.service';
import { User, Meal } from '../../types/database.types';

interface MealCountData {
  breakfast: number;
  lunch: number;
  dinner: number;
  guestBreakfast: number;
  guestLunch: number;
  guestDinner: number;
}

interface StudentMealData {
  user: User;
  meal: Meal | null;
}

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const [todayMealCounts, setTodayMealCounts] = useState<MealCountData>({
    breakfast: 0,
    lunch: 0,
    dinner: 0,
    guestBreakfast: 0,
    guestLunch: 0,
    guestDinner: 0,
  });
  const [tomorrowMealCounts, setTomorrowMealCounts] = useState<MealCountData>({
    breakfast: 0,
    lunch: 0,
    dinner: 0,
    guestBreakfast: 0,
    guestLunch: 0,
    guestDinner: 0,
  });

  const [todayStudents, setTodayStudents] = useState<StudentMealData[]>([]);
  const [tomorrowStudents, setTomorrowStudents] = useState<StudentMealData[]>([]);
  const [activeStudentsCount, setActiveStudentsCount] = useState(0);
  const [pendingDepositsCount, setPendingDepositsCount] = useState(0);
  const [todayExpenses, setTodayExpenses] = useState(0);

  const today = new Date().toISOString().split('T')[0];
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
  const currentMonth = new Date().toISOString().slice(0, 7);

  const fetchDashboardData = async () => {
    try {
      setError(null);

      // Fetch today's meals
      const todayMealsResult = await getMealsByDate(today);
      if (!todayMealsResult.success) {
        throw new Error(todayMealsResult.error || 'Failed to fetch today\'s meals');
      }

      // Fetch tomorrow's meals
      const tomorrowMealsResult = await getMealsByDate(tomorrow);
      if (!tomorrowMealsResult.success) {
        throw new Error(tomorrowMealsResult.error || 'Failed to fetch tomorrow\'s meals');
      }

      // Fetch all users
      const usersResult = await getAllUsers();
      if (!usersResult.success) {
        throw new Error(usersResult.error || 'Failed to fetch users');
      }

      const users = usersResult.data || [];
      const activeUsers = users.filter((u) => u.is_active && u.role === 'student');
      setActiveStudentsCount(activeUsers.length);

      // Calculate today's meal counts
      const todayMeals = todayMealsResult.data || [];
      const todayCounts = calculateMealCounts(todayMeals);
      setTodayMealCounts(todayCounts);

      // Calculate tomorrow's meal counts
      const tomorrowMeals = tomorrowMealsResult.data || [];
      const tomorrowCounts = calculateMealCounts(tomorrowMeals);
      setTomorrowMealCounts(tomorrowCounts);

      // Map students with their meal data
      const todayStudentData = mapStudentsWithMeals(activeUsers, todayMeals);
      setTodayStudents(todayStudentData);

      const tomorrowStudentData = mapStudentsWithMeals(activeUsers, tomorrowMeals);
      setTomorrowStudents(tomorrowStudentData);

      // Fetch deposits to calculate pending
      const depositsResult = await getDepositsByMonth(currentMonth);
      if (depositsResult.success) {
        const deposits = depositsResult.data || [];
        const usersWithDeposits = new Set(deposits.map((d) => d.user_id));
        const pending = activeUsers.filter((u) => !usersWithDeposits.has(u.id));
        setPendingDepositsCount(pending.length);
      }

      // Fetch today's expenses
      const expensesResult = await getTotalExpensesByMonth(currentMonth);
      if (expensesResult.success) {
        setTodayExpenses(expensesResult.data || 0);
      }

      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const calculateMealCounts = (meals: Meal[]): MealCountData => {
    return meals.reduce(
      (acc, meal) => ({
        breakfast: acc.breakfast + (meal.breakfast ? 1 : 0),
        lunch: acc.lunch + (meal.lunch ? 1 : 0),
        dinner: acc.dinner + (meal.dinner ? 1 : 0),
        guestBreakfast: acc.guestBreakfast + (meal.guest_breakfast || 0),
        guestLunch: acc.guestLunch + (meal.guest_lunch || 0),
        guestDinner: acc.guestDinner + (meal.guest_dinner || 0),
      }),
      {
        breakfast: 0,
        lunch: 0,
        dinner: 0,
        guestBreakfast: 0,
        guestLunch: 0,
        guestDinner: 0,
      }
    );
  };

  const mapStudentsWithMeals = (users: User[], meals: Meal[]): StudentMealData[] => {
    const mealsByUser = new Map(meals.map((m) => [m.user_id, m]));
    return users.map((user) => ({
      user,
      meal: mealsByUser.get(user.id) || null,
    }));
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
  };

  const handleExportMealList = () => {
    // Create CSV content
    const headers = ['Name', 'Room', 'Breakfast', 'Lunch', 'Dinner', 'Guest B', 'Guest L', 'Guest D'];
    const rows = todayStudents
      .filter((s) => s.meal && (s.meal.breakfast || s.meal.lunch || s.meal.dinner))
      .map((s) => [
        s.user.full_name,
        s.user.room_number || 'N/A',
        s.meal?.breakfast ? 'Yes' : 'No',
        s.meal?.lunch ? 'Yes' : 'No',
        s.meal?.dinner ? 'Yes' : 'No',
        s.meal?.guest_breakfast || 0,
        s.meal?.guest_lunch || 0,
        s.meal?.guest_dinner || 0,
      ]);

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `meal-list-${today}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  useEffect(() => {
    fetchDashboardData();

    // Auto-refresh every minute
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <EmptyState
          icon={AlertCircle}
          title="Error Loading Dashboard"
          description={error}
          action={{
            label: 'Retry',
            onClick: fetchDashboardData,
          }}
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Manager Dashboard</h1>
          <p className="text-gray-600 mt-1 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Last updated: {lastUpdated.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={refreshing}
            leftIcon={<RefreshCw className="w-4 h-4" />}
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
          <Button onClick={handleExportMealList} leftIcon={<Download className="w-4 h-4" />}>
            Export Today's List
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Students"
          value={activeStudentsCount}
          icon={Users}
          color="blue"
          description="Currently enrolled"
        />
        <StatCard
          title="Pending Deposits"
          value={pendingDepositsCount}
          icon={AlertCircle}
          color={pendingDepositsCount > 0 ? 'red' : 'green'}
          description={`For ${currentMonth}`}
        />
        <StatCard
          title="Monthly Expenses"
          value={`$${todayExpenses.toFixed(2)}`}
          icon={DollarSign}
          color="purple"
          description={`Total for ${currentMonth}`}
        />
        <StatCard
          title="Today's Total Meals"
          value={todayMealCounts.breakfast + todayMealCounts.lunch + todayMealCounts.dinner}
          icon={TrendingUp}
          color="green"
          description="Across all meal times"
        />
      </div>

      {/* Today's Meal Counts */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Today's Meals ({today})</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start gap-4">
            <div className="bg-yellow-50 rounded-lg p-3">
              <Coffee className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Breakfast</p>
              <p className="text-2xl font-bold text-gray-900">{todayMealCounts.breakfast}</p>
              {todayMealCounts.guestBreakfast > 0 && (
                <p className="text-sm text-gray-500">+{todayMealCounts.guestBreakfast} guests</p>
              )}
            </div>
          </div>

          <div className="flex items-start gap-4">
            <div className="bg-orange-50 rounded-lg p-3">
              <UtensilsCrossed className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Lunch</p>
              <p className="text-2xl font-bold text-gray-900">{todayMealCounts.lunch}</p>
              {todayMealCounts.guestLunch > 0 && (
                <p className="text-sm text-gray-500">+{todayMealCounts.guestLunch} guests</p>
              )}
            </div>
          </div>

          <div className="flex items-start gap-4">
            <div className="bg-indigo-50 rounded-lg p-3">
              <Moon className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Dinner</p>
              <p className="text-2xl font-bold text-gray-900">{todayMealCounts.dinner}</p>
              {todayMealCounts.guestDinner > 0 && (
                <p className="text-sm text-gray-500">+{todayMealCounts.guestDinner} guests</p>
              )}
            </div>
          </div>
        </div>

        {/* Today's Student List */}
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Students Eating Today</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Room
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Breakfast
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Lunch
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dinner
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Guests
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {todayStudents
                  .filter((s) => s.meal && (s.meal.breakfast || s.meal.lunch || s.meal.dinner))
                  .map((studentData) => (
                    <tr key={studentData.user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {studentData.user.full_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {studentData.user.room_number || 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        {studentData.meal?.breakfast ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Yes
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            No
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        {studentData.meal?.lunch ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Yes
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            No
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        {studentData.meal?.dinner ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Yes
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            No
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="text-sm text-gray-900">
                          {(studentData.meal?.guest_breakfast || 0) +
                            (studentData.meal?.guest_lunch || 0) +
                            (studentData.meal?.guest_dinner || 0)}
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
            {todayStudents.filter((s) => s.meal && (s.meal.breakfast || s.meal.lunch || s.meal.dinner))
              .length === 0 && (
              <div className="text-center py-8 text-gray-500">No students eating today</div>
            )}
          </div>
        </div>
      </div>

      {/* Tomorrow's Preview */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Tomorrow's Preview ({tomorrow})</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Coffee className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{tomorrowMealCounts.breakfast}</p>
            <p className="text-sm text-gray-600">Breakfast</p>
            {tomorrowMealCounts.guestBreakfast > 0 && (
              <p className="text-xs text-gray-500 mt-1">+{tomorrowMealCounts.guestBreakfast} guests</p>
            )}
          </div>

          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <UtensilsCrossed className="w-8 h-8 text-orange-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{tomorrowMealCounts.lunch}</p>
            <p className="text-sm text-gray-600">Lunch</p>
            {tomorrowMealCounts.guestLunch > 0 && (
              <p className="text-xs text-gray-500 mt-1">+{tomorrowMealCounts.guestLunch} guests</p>
            )}
          </div>

          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Moon className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{tomorrowMealCounts.dinner}</p>
            <p className="text-sm text-gray-600">Dinner</p>
            {tomorrowMealCounts.guestDinner > 0 && (
              <p className="text-xs text-gray-500 mt-1">+{tomorrowMealCounts.guestDinner} guests</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
