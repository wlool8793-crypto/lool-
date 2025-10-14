import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Coffee,
  UtensilsCrossed,
  Moon,
  Lock,
  Users,
  Save,
  Loader2,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { getCurrentUser } from '../../services/auth.service';
import { getMealsByUser, upsertMeal } from '../../services/meals.service';
import { getSettingsByMonth } from '../../services/settings.service';
import { Meal, MealSettings } from '../../types/database.types';
import toast from 'react-hot-toast';
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameMonth,
  addMonths,
  subMonths,
  isBefore,
  startOfDay,
  setHours,
} from 'date-fns';

interface DayMeal {
  date: Date;
  meal?: Meal;
  isLocked: {
    breakfast: boolean;
    lunch: boolean;
    dinner: boolean;
  };
}

const MealPlanner: React.FC = () => {
  const navigate = useNavigate();
  const [userId, setUserId] = useState<string>('');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [dayMeals, setDayMeals] = useState<DayMeal[]>([]);
  const [mealSettings, setMealSettings] = useState<MealSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [pendingChanges, setPendingChanges] = useState<Map<string, Partial<Meal>>>(new Map());

  useEffect(() => {
    loadUserAndMeals();
  }, [currentDate]);

  const loadUserAndMeals = async () => {
    setIsLoading(true);

    try {
      const userResult = await getCurrentUser();
      if (!userResult.success || !userResult.data) {
        toast.error('Failed to load user data');
        navigate('/login');
        return;
      }

      setUserId(userResult.data.id);
      await loadMealsForMonth(userResult.data.id);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load meal planner');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMealsForMonth = async (userId: string) => {
    const monthStr = format(currentDate, 'yyyy-MM');

    // Load meal settings
    const settingsResult = await getSettingsByMonth(monthStr);
    if (settingsResult.success) {
      setMealSettings(settingsResult.data);
    }

    // Load meals for the month
    const startDate = format(startOfMonth(currentDate), 'yyyy-MM-dd');
    const endDate = format(endOfMonth(currentDate), 'yyyy-MM-dd');
    const mealsResult = await getMealsByUser(userId, startDate, endDate);

    if (mealsResult.success && mealsResult.data) {
      const meals = mealsResult.data;
      const days = eachDayOfInterval({
        start: startOfMonth(currentDate),
        end: endOfMonth(currentDate),
      });

      const dayMealsData: DayMeal[] = days.map((day) => {
        const dateStr = format(day, 'yyyy-MM-dd');
        const meal = meals.find((m) => m.meal_date === dateStr);

        return {
          date: day,
          meal,
          isLocked: {
            breakfast: meal?.breakfast_locked || checkIfLocked(day, 'breakfast'),
            lunch: meal?.lunch_locked || checkIfLocked(day, 'lunch'),
            dinner: meal?.dinner_locked || checkIfLocked(day, 'dinner'),
          },
        };
      });

      setDayMeals(dayMealsData);
    }
  };

  const checkIfLocked = (date: Date, mealType: 'breakfast' | 'lunch' | 'dinner'): boolean => {
    if (!mealSettings) return false;

    const now = new Date();
    const mealDate = startOfDay(date);

    let deadlineHour: number;
    let deadlineDate: Date;

    switch (mealType) {
      case 'breakfast':
        // Breakfast deadline is the previous day at specified hour
        deadlineDate = new Date(mealDate);
        deadlineDate.setDate(deadlineDate.getDate() - 1);
        deadlineHour = mealSettings.breakfast_deadline_hour;
        break;
      case 'lunch':
        // Lunch deadline is same day at specified hour
        deadlineDate = new Date(mealDate);
        deadlineHour = mealSettings.lunch_deadline_hour;
        break;
      case 'dinner':
        // Dinner deadline is same day at specified hour (or previous day if setting enabled)
        deadlineDate = new Date(mealDate);
        if (mealSettings.dinner_deadline_previous_day) {
          deadlineDate.setDate(deadlineDate.getDate() - 1);
        }
        deadlineHour = mealSettings.dinner_deadline_hour;
        break;
      default:
        return false;
    }

    const deadline = setHours(deadlineDate, deadlineHour);
    return isBefore(deadline, now);
  };

  const handleMealToggle = (date: Date, mealType: 'breakfast' | 'lunch' | 'dinner') => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const dayMeal = dayMeals.find((dm) => format(dm.date, 'yyyy-MM-dd') === dateStr);

    if (!dayMeal || dayMeal.isLocked[mealType]) {
      toast.error(`${mealType} is locked and cannot be changed`);
      return;
    }

    const currentMeal = dayMeal.meal || {
      user_id: userId,
      meal_date: dateStr,
      breakfast: false,
      lunch: false,
      dinner: false,
      breakfast_locked: false,
      lunch_locked: false,
      dinner_locked: false,
      guest_breakfast: 0,
      guest_lunch: 0,
      guest_dinner: 0,
    };

    const updatedMeal = {
      ...currentMeal,
      [mealType]: !currentMeal[mealType],
    };

    // Update local state
    setDayMeals((prev) =>
      prev.map((dm) =>
        format(dm.date, 'yyyy-MM-dd') === dateStr
          ? { ...dm, meal: updatedMeal as Meal }
          : dm
      )
    );

    // Track pending changes
    setPendingChanges((prev) => {
      const newChanges = new Map(prev);
      newChanges.set(dateStr, updatedMeal);
      return newChanges;
    });

    setHasChanges(true);
  };

  const handleGuestMealChange = (
    date: Date,
    mealType: 'guest_breakfast' | 'guest_lunch' | 'guest_dinner',
    value: number
  ) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const dayMeal = dayMeals.find((dm) => format(dm.date, 'yyyy-MM-dd') === dateStr);

    if (!dayMeal) return;

    const currentMeal = dayMeal.meal || {
      user_id: userId,
      meal_date: dateStr,
      breakfast: false,
      lunch: false,
      dinner: false,
      breakfast_locked: false,
      lunch_locked: false,
      dinner_locked: false,
      guest_breakfast: 0,
      guest_lunch: 0,
      guest_dinner: 0,
    };

    const updatedMeal = {
      ...currentMeal,
      [mealType]: Math.max(0, value),
    };

    setDayMeals((prev) =>
      prev.map((dm) =>
        format(dm.date, 'yyyy-MM-dd') === dateStr
          ? { ...dm, meal: updatedMeal as Meal }
          : dm
      )
    );

    setPendingChanges((prev) => {
      const newChanges = new Map(prev);
      newChanges.set(dateStr, updatedMeal);
      return newChanges;
    });

    setHasChanges(true);
  };

  const handleSaveChanges = async () => {
    if (pendingChanges.size === 0) {
      toast('No changes to save', { icon: 'ℹ️' });
      return;
    }

    setIsSaving(true);

    try {
      const promises = Array.from(pendingChanges.entries()).map(([dateStr, mealData]) => {
        return upsertMeal({
          user_id: userId,
          meal_date: dateStr,
          breakfast: mealData.breakfast || false,
          lunch: mealData.lunch || false,
          dinner: mealData.dinner || false,
          breakfast_locked: mealData.breakfast_locked || false,
          lunch_locked: mealData.lunch_locked || false,
          dinner_locked: mealData.dinner_locked || false,
          guest_breakfast: mealData.guest_breakfast || 0,
          guest_lunch: mealData.guest_lunch || 0,
          guest_dinner: mealData.guest_dinner || 0,
        });
      });

      const results = await Promise.all(promises);
      const allSuccess = results.every((r) => r.success);

      if (allSuccess) {
        toast.success('Meals saved successfully!');
        setPendingChanges(new Map());
        setHasChanges(false);
        await loadMealsForMonth(userId);
      } else {
        toast.error('Some meals failed to save. Please try again.');
      }
    } catch (error) {
      console.error('Error saving meals:', error);
      toast.error('Failed to save meals');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePreviousMonth = () => {
    setCurrentDate(subMonths(currentDate, 1));
    setPendingChanges(new Map());
    setHasChanges(false);
  };

  const handleNextMonth = () => {
    setCurrentDate(addMonths(currentDate, 1));
    setPendingChanges(new Map());
    setHasChanges(false);
  };

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading meal planner...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <Calendar className="w-7 h-7 mr-3 text-indigo-600" />
                Meal Planner
              </h1>
              <p className="text-gray-600 mt-1">Plan your meals for the month</p>
            </div>
            <button
              onClick={handleSaveChanges}
              disabled={!hasChanges || isSaving}
              className="flex items-center px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? (
                <>
                  <Loader2 className="animate-spin w-5 h-5 mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5 mr-2" />
                  Save Changes
                </>
              )}
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

        {/* Legend */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm">
            <div className="flex items-center">
              <Coffee className="w-4 h-4 text-amber-600 mr-2" />
              <span className="text-gray-700">Breakfast</span>
            </div>
            <div className="flex items-center">
              <UtensilsCrossed className="w-4 h-4 text-orange-600 mr-2" />
              <span className="text-gray-700">Lunch</span>
            </div>
            <div className="flex items-center">
              <Moon className="w-4 h-4 text-indigo-600 mr-2" />
              <span className="text-gray-700">Dinner</span>
            </div>
            <div className="flex items-center">
              <Lock className="w-4 h-4 text-red-600 mr-2" />
              <span className="text-gray-700">Locked</span>
            </div>
            <div className="flex items-center">
              <Users className="w-4 h-4 text-purple-600 mr-2" />
              <span className="text-gray-700">Guest Meals</span>
            </div>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Week Day Headers */}
          <div className="grid grid-cols-7 bg-gray-50 border-b">
            {weekDays.map((day) => (
              <div
                key={day}
                className="py-3 text-center text-sm font-semibold text-gray-700"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Days */}
          <div className="grid grid-cols-7 divide-x divide-y">
            {/* Empty cells for days before month starts */}
            {Array.from({ length: startOfMonth(currentDate).getDay() }).map((_, idx) => (
              <div key={`empty-${idx}`} className="min-h-32 bg-gray-50"></div>
            ))}

            {/* Actual days */}
            {dayMeals.map((dayMeal) => {
              const isCurrentMonth = isSameMonth(dayMeal.date, currentDate);
              const isPast = isBefore(dayMeal.date, startOfDay(new Date()));

              return (
                <div
                  key={format(dayMeal.date, 'yyyy-MM-dd')}
                  className={`min-h-32 p-2 ${
                    !isCurrentMonth ? 'bg-gray-50' : ''
                  } ${isPast ? 'opacity-60' : ''}`}
                >
                  <div className="text-right mb-2">
                    <span
                      className={`text-sm font-medium ${
                        isCurrentMonth ? 'text-gray-900' : 'text-gray-400'
                      }`}
                    >
                      {format(dayMeal.date, 'd')}
                    </span>
                  </div>

                  {isCurrentMonth && (
                    <div className="space-y-2">
                      {/* Breakfast */}
                      <button
                        onClick={() => handleMealToggle(dayMeal.date, 'breakfast')}
                        disabled={dayMeal.isLocked.breakfast}
                        className={`w-full flex items-center justify-between px-2 py-1 rounded text-xs ${
                          dayMeal.meal?.breakfast
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-gray-100 text-gray-600'
                        } ${
                          dayMeal.isLocked.breakfast
                            ? 'cursor-not-allowed opacity-50'
                            : 'hover:opacity-80'
                        }`}
                      >
                        <Coffee className="w-3 h-3" />
                        {dayMeal.isLocked.breakfast && <Lock className="w-3 h-3" />}
                      </button>

                      {/* Lunch */}
                      <button
                        onClick={() => handleMealToggle(dayMeal.date, 'lunch')}
                        disabled={dayMeal.isLocked.lunch}
                        className={`w-full flex items-center justify-between px-2 py-1 rounded text-xs ${
                          dayMeal.meal?.lunch
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-gray-100 text-gray-600'
                        } ${
                          dayMeal.isLocked.lunch
                            ? 'cursor-not-allowed opacity-50'
                            : 'hover:opacity-80'
                        }`}
                      >
                        <UtensilsCrossed className="w-3 h-3" />
                        {dayMeal.isLocked.lunch && <Lock className="w-3 h-3" />}
                      </button>

                      {/* Dinner */}
                      <button
                        onClick={() => handleMealToggle(dayMeal.date, 'dinner')}
                        disabled={dayMeal.isLocked.dinner}
                        className={`w-full flex items-center justify-between px-2 py-1 rounded text-xs ${
                          dayMeal.meal?.dinner
                            ? 'bg-indigo-100 text-indigo-800'
                            : 'bg-gray-100 text-gray-600'
                        } ${
                          dayMeal.isLocked.dinner
                            ? 'cursor-not-allowed opacity-50'
                            : 'hover:opacity-80'
                        }`}
                      >
                        <Moon className="w-3 h-3" />
                        {dayMeal.isLocked.dinner && <Lock className="w-3 h-3" />}
                      </button>

                      {/* Guest count indicator */}
                      {((dayMeal.meal?.guest_breakfast || 0) +
                        (dayMeal.meal?.guest_lunch || 0) +
                        (dayMeal.meal?.guest_dinner || 0)) > 0 && (
                        <div className="flex items-center justify-center text-xs text-purple-600">
                          <Users className="w-3 h-3 mr-1" />
                          {(dayMeal.meal?.guest_breakfast || 0) +
                            (dayMeal.meal?.guest_lunch || 0) +
                            (dayMeal.meal?.guest_dinner || 0)}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Deadline Information */}
        {mealSettings && (
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium text-blue-800">Meal Deadlines</h3>
                <ul className="text-sm text-blue-700 mt-2 space-y-1">
                  <li>
                    Breakfast: {mealSettings.breakfast_deadline_hour}:00 (previous day)
                  </li>
                  <li>Lunch: {mealSettings.lunch_deadline_hour}:00 (same day)</li>
                  <li>
                    Dinner: {mealSettings.dinner_deadline_hour}:00 (
                    {mealSettings.dinner_deadline_previous_day ? 'previous' : 'same'} day)
                  </li>
                  <li className="text-red-700 font-medium">
                    Late cancellation penalty: Rs. {mealSettings.late_cancellation_penalty}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Unsaved Changes Warning */}
        {hasChanges && (
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-yellow-800">Unsaved Changes</h3>
                  <p className="text-sm text-yellow-700 mt-1">
                    You have {pendingChanges.size} unsaved meal changes. Don't forget to save!
                  </p>
                </div>
              </div>
              <button
                onClick={handleSaveChanges}
                disabled={isSaving}
                className="ml-4 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50"
              >
                Save Now
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MealPlanner;
