/**
 * Meal deadline configurations
 * Default deadlines for meal selections in the Hostel Meal Management System
 */

/**
 * Meal types available in the system
 */
export enum MealType {
  BREAKFAST = 'breakfast',
  LUNCH = 'lunch',
  DINNER = 'dinner',
}

/**
 * Deadline configuration for a specific meal
 */
export interface DeadlineConfig {
  /**
   * Hour of the deadline (0-23)
   */
  hour: number;

  /**
   * Minute of the deadline (0-59)
   */
  minute: number;

  /**
   * Number of days before the meal (0 for same day, 1 for previous day)
   */
  daysBefore: number;
}

/**
 * Default deadline configurations for each meal type
 *
 * Rules:
 * - Breakfast: Must be selected before 10 PM the previous day
 * - Lunch: Must be selected before 10 AM the same day
 * - Dinner: Must be selected before 5 PM the same day
 */
export const DEFAULT_DEADLINES: Record<MealType, DeadlineConfig> = {
  [MealType.BREAKFAST]: {
    hour: 22, // 10 PM
    minute: 0,
    daysBefore: 1, // Previous day
  },
  [MealType.LUNCH]: {
    hour: 10, // 10 AM
    minute: 0,
    daysBefore: 0, // Same day
  },
  [MealType.DINNER]: {
    hour: 17, // 5 PM
    minute: 0,
    daysBefore: 0, // Same day
  },
};

/**
 * Meal time ranges (when meals are typically served)
 * Used for display purposes and validation
 */
export const MEAL_TIME_RANGES = {
  [MealType.BREAKFAST]: {
    start: { hour: 7, minute: 0 }, // 7:00 AM
    end: { hour: 9, minute: 30 },   // 9:30 AM
  },
  [MealType.LUNCH]: {
    start: { hour: 12, minute: 0 }, // 12:00 PM
    end: { hour: 14, minute: 30 },  // 2:30 PM
  },
  [MealType.DINNER]: {
    start: { hour: 19, minute: 0 }, // 7:00 PM
    end: { hour: 21, minute: 30 },  // 9:30 PM
  },
} as const;

/**
 * Buffer time in minutes before deadline for warnings
 * Show warning when deadline is within this time
 */
export const DEADLINE_WARNING_BUFFER_MINUTES = 60; // 1 hour

/**
 * Maximum days in advance that meals can be selected
 */
export const MAX_ADVANCE_SELECTION_DAYS = 30;

/**
 * Minimum days in past that meal history can be viewed
 */
export const MAX_HISTORY_DAYS = 90;

/**
 * Get a human-readable description of a deadline
 * @param mealType - The type of meal
 * @returns Human-readable deadline description
 */
export const getDeadlineDescription = (mealType: MealType): string => {
  const deadline = DEFAULT_DEADLINES[mealType];
  const hour12 = deadline.hour > 12 ? deadline.hour - 12 : deadline.hour;
  const ampm = deadline.hour >= 12 ? 'PM' : 'AM';
  const timeStr = `${hour12}:${deadline.minute.toString().padStart(2, '0')} ${ampm}`;

  if (deadline.daysBefore === 1) {
    return `${timeStr} the previous day`;
  } else if (deadline.daysBefore === 0) {
    return `${timeStr} on the same day`;
  } else {
    return `${timeStr}, ${deadline.daysBefore} days before`;
  }
};

/**
 * Get formatted meal time range
 * @param mealType - The type of meal
 * @returns Formatted time range string
 */
export const getMealTimeRange = (mealType: MealType): string => {
  const range = MEAL_TIME_RANGES[mealType];

  const formatTime = (hour: number, minute: number): string => {
    const hour12 = hour > 12 ? hour - 12 : hour || 12;
    const ampm = hour >= 12 ? 'PM' : 'AM';
    return `${hour12}:${minute.toString().padStart(2, '0')} ${ampm}`;
  };

  return `${formatTime(range.start.hour, range.start.minute)} - ${formatTime(range.end.hour, range.end.minute)}`;
};
