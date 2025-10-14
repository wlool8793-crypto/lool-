import React, { useMemo } from 'react';
import { ChevronLeft, ChevronRight, Clock, AlertCircle } from 'lucide-react';
import { MealToggle, MealType } from './MealToggle';

export interface MealStatus {
  breakfast: boolean;
  lunch: boolean;
  dinner: boolean;
  breakfastLocked: boolean;
  lunchLocked: boolean;
  dinnerLocked: boolean;
  breakfastGuests?: number;
  lunchGuests?: number;
  dinnerGuests?: number;
  deadlineStatus?: 'safe' | 'warning' | 'critical';
}

export interface MealCalendarProps {
  month: number; // 0-11
  year: number;
  mealStatuses: Record<string, MealStatus>; // key: 'YYYY-MM-DD'
  onMealToggle: (date: string, mealType: MealType) => void;
  onGuestClick?: (date: string, mealType: MealType) => void;
  onMonthChange: (month: number, year: number) => void;
  deadlineHours?: number; // Hours before meal deadline
}

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export const MealCalendar: React.FC<MealCalendarProps> = ({
  month,
  year,
  mealStatuses,
  onMealToggle,
  onGuestClick,
  onMonthChange,
  deadlineHours = 24,
}) => {
  // Calculate calendar data
  const calendarData = useMemo(() => {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: Array<{ date: number; dateString: string; isCurrentMonth: boolean }> = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push({ date: 0, dateString: '', isCurrentMonth: false });
    }

    // Add days of the month
    for (let date = 1; date <= daysInMonth; date++) {
      const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
      days.push({ date, dateString, isCurrentMonth: true });
    }

    return days;
  }, [month, year]);

  const handlePrevMonth = () => {
    if (month === 0) {
      onMonthChange(11, year - 1);
    } else {
      onMonthChange(month - 1, year);
    }
  };

  const handleNextMonth = () => {
    if (month === 11) {
      onMonthChange(0, year + 1);
    } else {
      onMonthChange(month + 1, year);
    }
  };

  const getDeadlineStatus = (dateString: string): 'safe' | 'warning' | 'critical' => {
    const date = new Date(dateString);
    const now = new Date();
    const hoursUntil = (date.getTime() - now.getTime()) / (1000 * 60 * 60);

    if (hoursUntil < deadlineHours / 3) return 'critical';
    if (hoursUntil < deadlineHours * 2 / 3) return 'warning';
    return 'safe';
  };

  const isToday = (dateString: string): boolean => {
    const today = new Date();
    const todayString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    return dateString === todayString;
  };

  const isPast = (dateString: string): boolean => {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-gray-800">
            {MONTH_NAMES[month]} {year}
          </h2>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>Deadline: {deadlineHours}h before</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevMonth}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Previous month"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={handleNextMonth}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Next month"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-6 mb-4 p-3 bg-gray-50 rounded-lg text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border-2 border-green-500 bg-green-50"></div>
          <span>Safe</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border-2 border-yellow-500 bg-yellow-50"></div>
          <span>Deadline Soon</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border-2 border-red-500 bg-red-50"></div>
          <span>Critical</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-gray-200 opacity-50"></div>
          <span>Locked</span>
        </div>
      </div>

      {/* Days of Week Header */}
      <div className="grid grid-cols-7 gap-2 mb-2">
        {DAYS_OF_WEEK.map((day) => (
          <div
            key={day}
            className="text-center font-semibold text-sm text-gray-600 py-2"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2">
        {calendarData.map((day, index) => {
          if (!day.isCurrentMonth) {
            return <div key={index} className="min-h-[140px]" />;
          }

          const mealStatus = mealStatuses[day.dateString] || {
            breakfast: false,
            lunch: false,
            dinner: false,
            breakfastLocked: isPast(day.dateString),
            lunchLocked: isPast(day.dateString),
            dinnerLocked: isPast(day.dateString),
          };

          const today = isToday(day.dateString);
          const past = isPast(day.dateString);
          const deadlineStatus = getDeadlineStatus(day.dateString);

          return (
            <div
              key={day.dateString}
              className={`
                min-h-[140px] p-2 border-2 rounded-lg transition-all
                ${today ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200'}
                ${past && !today ? 'bg-gray-50' : 'bg-white'}
                hover:shadow-lg
              `}
            >
              {/* Date Header */}
              <div className="flex items-center justify-between mb-2">
                <span className={`text-sm font-bold ${today ? 'text-blue-600' : 'text-gray-700'}`}>
                  {day.date}
                </span>
                {today && (
                  <span className="px-2 py-0.5 text-xs font-medium bg-blue-500 text-white rounded-full">
                    Today
                  </span>
                )}
                {past && !today && (
                  <span className="text-xs text-gray-400">Past</span>
                )}
              </div>

              {/* Meal Toggles */}
              <div className="space-y-1.5">
                <MealToggle
                  mealType="breakfast"
                  isOn={mealStatus.breakfast}
                  isLocked={mealStatus.breakfastLocked}
                  guestCount={mealStatus.breakfastGuests}
                  deadlineStatus={deadlineStatus}
                  onToggle={() => onMealToggle(day.dateString, 'breakfast')}
                  onGuestClick={() => onGuestClick?.(day.dateString, 'breakfast')}
                />
                <MealToggle
                  mealType="lunch"
                  isOn={mealStatus.lunch}
                  isLocked={mealStatus.lunchLocked}
                  guestCount={mealStatus.lunchGuests}
                  deadlineStatus={deadlineStatus}
                  onToggle={() => onMealToggle(day.dateString, 'lunch')}
                  onGuestClick={() => onGuestClick?.(day.dateString, 'lunch')}
                />
                <MealToggle
                  mealType="dinner"
                  isOn={mealStatus.dinner}
                  isLocked={mealStatus.dinnerLocked}
                  guestCount={mealStatus.dinnerGuests}
                  deadlineStatus={deadlineStatus}
                  onToggle={() => onMealToggle(day.dateString, 'dinner')}
                  onGuestClick={() => onGuestClick?.(day.dateString, 'dinner')}
                />
              </div>

              {/* Warnings */}
              {!past && deadlineStatus === 'critical' && (
                <div className="mt-2 flex items-center gap-1 text-xs text-red-600">
                  <AlertCircle className="w-3 h-3" />
                  <span>Deadline soon!</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MealCalendar;
