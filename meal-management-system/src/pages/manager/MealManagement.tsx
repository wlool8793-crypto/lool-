import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Coffee,
  UtensilsCrossed,
  Moon,
  Users,
  Download,
  Filter,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  TrendingUp,
  Eye,
  X,
} from 'lucide-react';
import { Button } from '../../components/forms/Button';
import { Input } from '../../components/forms/Input';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { getMealsByDate, getMealsByDateRange } from '../../services/meals.service';
import { getAllUsers } from '../../services/users.service';
import { Meal, User } from '../../types/database.types';
import toast from 'react-hot-toast';

interface MealWithUser extends Meal {
  user?: User;
}

interface MealCounts {
  breakfast: number;
  lunch: number;
  dinner: number;
  guestBreakfast: number;
  guestLunch: number;
  guestDinner: number;
  totalStudents: number;
}

export const MealManagement: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [meals, setMeals] = useState<MealWithUser[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [mealCounts, setMealCounts] = useState<MealCounts>({
    breakfast: 0,
    lunch: 0,
    dinner: 0,
    guestBreakfast: 0,
    guestLunch: 0,
    guestDinner: 0,
    totalStudents: 0,
  });

  // Date range filter
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedMeal, setSelectedMeal] = useState<MealWithUser | null>(null);

  const fetchUsers = async () => {
    try {
      const result = await getAllUsers();

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch users');
      }

      setUsers(result.data || []);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch users');
    }
  };

  const fetchMeals = async () => {
    try {
      setLoading(true);
      let result;

      if (startDate && endDate) {
        result = await getMealsByDateRange(startDate, endDate);
      } else {
        result = await getMealsByDate(selectedDate);
      }

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch meals');
      }

      const mealsList = result.data || [];

      // Enrich meals with user data
      const enrichedMeals = mealsList.map((meal) => ({
        ...meal,
        user: users.find((u) => u.id === meal.user_id),
      }));

      setMeals(enrichedMeals);

      // Calculate counts
      const counts = mealsList.reduce(
        (acc, meal) => ({
          breakfast: acc.breakfast + (meal.breakfast ? 1 : 0),
          lunch: acc.lunch + (meal.lunch ? 1 : 0),
          dinner: acc.dinner + (meal.dinner ? 1 : 0),
          guestBreakfast: acc.guestBreakfast + (meal.guest_breakfast || 0),
          guestLunch: acc.guestLunch + (meal.guest_lunch || 0),
          guestDinner: acc.guestDinner + (meal.guest_dinner || 0),
          totalStudents: acc.totalStudents + 1,
        }),
        {
          breakfast: 0,
          lunch: 0,
          dinner: 0,
          guestBreakfast: 0,
          guestLunch: 0,
          guestDinner: 0,
          totalStudents: 0,
        }
      );

      setMealCounts(counts);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch meals');
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (days: number) => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() + days);
    const newDate = date.toISOString().split('T')[0];
    setSelectedDate(newDate);
    setStartDate('');
    setEndDate('');
  };

  const handleExport = () => {
    const dateRange = startDate && endDate ? `${startDate}_to_${endDate}` : selectedDate;
    const headers = ['Date', 'Student', 'Room', 'Email', 'Breakfast', 'Lunch', 'Dinner', 'Guest B', 'Guest L', 'Guest D', 'Total Meals'];
    const rows = meals.map((m) => [
      m.meal_date,
      m.user?.full_name || 'Unknown',
      m.user?.room_number || 'N/A',
      m.user?.email || 'N/A',
      m.breakfast ? 'Yes' : 'No',
      m.lunch ? 'Yes' : 'No',
      m.dinner ? 'Yes' : 'No',
      m.guest_breakfast || 0,
      m.guest_lunch || 0,
      m.guest_dinner || 0,
      (m.breakfast ? 1 : 0) + (m.lunch ? 1 : 0) + (m.dinner ? 1 : 0),
    ]);

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `meal-report-${dateRange}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('Report exported successfully');
  };

  const handleViewDetails = (meal: MealWithUser) => {
    setSelectedMeal(meal);
    setShowDetailsModal(true);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    if (users.length > 0) {
      fetchMeals();
    }
  }, [selectedDate, startDate, endDate, users]);

  if (loading && users.length === 0) {
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
          <h1 className="text-3xl font-bold text-gray-900">Meal Management</h1>
          <p className="text-gray-600 mt-1">View and analyze student meal planning</p>
        </div>
        <Button onClick={handleExport} leftIcon={<Download className="w-4 h-4" />}>
          Export Report
        </Button>
      </div>

      {/* Date Selector */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Select Date</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleDateChange(-1)}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value);
                  setStartDate('');
                  setEndDate('');
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => handleDateChange(1)}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
              <button
                onClick={() => {
                  setSelectedDate(new Date().toISOString().split('T')[0]);
                  setStartDate('');
                  setEndDate('');
                }}
                className="ml-2 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                Today
              </button>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Or Date Range</h3>
            <div className="flex items-center gap-2">
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                placeholder="Start"
              />
              <span className="text-gray-500">to</span>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                placeholder="End"
              />
            </div>
          </div>
        </div>

        {!startDate && !endDate && (
          <div className="text-center mt-4 py-2">
            <p className="text-xl font-bold text-gray-900">
              {new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Students</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{mealCounts.totalStudents}</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-3">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Meals</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {mealCounts.breakfast + mealCounts.lunch + mealCounts.dinner}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <UtensilsCrossed className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Guest Meals</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {mealCounts.guestBreakfast + mealCounts.guestLunch + mealCounts.guestDinner}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg per Student</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {mealCounts.totalStudents > 0
                  ? (
                      (mealCounts.breakfast + mealCounts.lunch + mealCounts.dinner) /
                      mealCounts.totalStudents
                    ).toFixed(1)
                  : '0'}
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-3">
              <Calendar className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Meal Counts by Type */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Meal Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start gap-4">
            <div className="bg-yellow-50 rounded-lg p-3">
              <Coffee className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Breakfast</p>
              <p className="text-2xl font-bold text-gray-900">{mealCounts.breakfast}</p>
              {mealCounts.guestBreakfast > 0 && (
                <p className="text-sm text-gray-500">+{mealCounts.guestBreakfast} guests</p>
              )}
            </div>
          </div>

          <div className="flex items-start gap-4">
            <div className="bg-orange-50 rounded-lg p-3">
              <UtensilsCrossed className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Lunch</p>
              <p className="text-2xl font-bold text-gray-900">{mealCounts.lunch}</p>
              {mealCounts.guestLunch > 0 && (
                <p className="text-sm text-gray-500">+{mealCounts.guestLunch} guests</p>
              )}
            </div>
          </div>

          <div className="flex items-start gap-4">
            <div className="bg-indigo-50 rounded-lg p-3">
              <Moon className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Dinner</p>
              <p className="text-2xl font-bold text-gray-900">{mealCounts.dinner}</p>
              {mealCounts.guestDinner > 0 && (
                <p className="text-sm text-gray-500">+{mealCounts.guestDinner} guests</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Students Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Student Meal Details</h3>
        </div>
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
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {meals.map((meal) => {
                const totalMeals = (meal.breakfast ? 1 : 0) + (meal.lunch ? 1 : 0) + (meal.dinner ? 1 : 0);
                const totalGuests =
                  (meal.guest_breakfast || 0) + (meal.guest_lunch || 0) + (meal.guest_dinner || 0);

                return (
                  <tr key={meal.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-medium text-sm">
                              {meal.user?.full_name
                                ?.split(' ')
                                .map((n) => n[0])
                                .join('')
                                .toUpperCase() || '?'}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {meal.user?.full_name || 'Unknown'}
                          </div>
                          <div className="text-sm text-gray-500">{meal.user?.email || 'N/A'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{meal.user?.room_number || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {meal.breakfast ? (
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
                      {meal.lunch ? (
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
                      {meal.dinner ? (
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
                      <div className="text-sm font-medium text-gray-900">{totalGuests}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="text-sm font-bold text-gray-900">{totalMeals}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <button
                        onClick={() => handleViewDetails(meal)}
                        className="text-blue-600 hover:text-blue-900"
                        title="View Details"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {meals.length === 0 && (
          <EmptyState
            icon={AlertCircle}
            title="No Meals Found"
            description="No students have opted for meals on the selected date"
          />
        )}
      </div>

      {/* Details Modal */}
      {showDetailsModal && selectedMeal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Meal Details</h2>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <p className="text-sm text-gray-600">Student</p>
                <p className="text-lg font-semibold text-gray-900">
                  {selectedMeal.user?.full_name || 'Unknown'}
                </p>
                <p className="text-sm text-gray-500">{selectedMeal.user?.email || 'N/A'}</p>
              </div>

              <div className="border-b border-gray-200 pb-4">
                <p className="text-sm text-gray-600">Date</p>
                <p className="text-lg font-semibold text-gray-900">
                  {new Date(selectedMeal.meal_date + 'T00:00:00').toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-700 mb-3">Meal Selections</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Breakfast</span>
                    <span
                      className={`font-medium ${
                        selectedMeal.breakfast ? 'text-green-600' : 'text-gray-400'
                      }`}
                    >
                      {selectedMeal.breakfast ? 'Yes' : 'No'}
                      {selectedMeal.guest_breakfast
                        ? ` (+${selectedMeal.guest_breakfast} guest${selectedMeal.guest_breakfast > 1 ? 's' : ''})`
                        : ''}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Lunch</span>
                    <span
                      className={`font-medium ${
                        selectedMeal.lunch ? 'text-green-600' : 'text-gray-400'
                      }`}
                    >
                      {selectedMeal.lunch ? 'Yes' : 'No'}
                      {selectedMeal.guest_lunch
                        ? ` (+${selectedMeal.guest_lunch} guest${selectedMeal.guest_lunch > 1 ? 's' : ''})`
                        : ''}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Dinner</span>
                    <span
                      className={`font-medium ${
                        selectedMeal.dinner ? 'text-green-600' : 'text-gray-400'
                      }`}
                    >
                      {selectedMeal.dinner ? 'Yes' : 'No'}
                      {selectedMeal.guest_dinner
                        ? ` (+${selectedMeal.guest_dinner} guest${selectedMeal.guest_dinner > 1 ? 's' : ''})`
                        : ''}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mt-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Total Meals</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {(selectedMeal.breakfast ? 1 : 0) +
                      (selectedMeal.lunch ? 1 : 0) +
                      (selectedMeal.dinner ? 1 : 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm font-medium text-gray-700">Total Guests</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {(selectedMeal.guest_breakfast || 0) +
                      (selectedMeal.guest_lunch || 0) +
                      (selectedMeal.guest_dinner || 0)}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <Button onClick={() => setShowDetailsModal(false)}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MealManagement;
