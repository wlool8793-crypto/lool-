/**
 * Deadline checking utilities for the Hostel Meal Management System
 * Handles meal selection deadline validation and time calculations
 */

import {
  MealType,
  DEFAULT_DEADLINES,
  DeadlineConfig,
  DEADLINE_WARNING_BUFFER_MINUTES,
} from '../constants/deadlines';

/**
 * Deadline check result interface
 */
export interface DeadlineCheckResult {
  /**
   * Whether the deadline has passed
   */
  isPassed: boolean;

  /**
   * Whether the meal should be locked (cannot be modified)
   */
  isLocked: boolean;

  /**
   * Time remaining until deadline in milliseconds (negative if passed)
   */
  timeRemaining: number;

  /**
   * Whether to show a warning (deadline approaching)
   */
  showWarning: boolean;

  /**
   * The actual deadline date/time
   */
  deadlineDate: Date;

  /**
   * Human-readable time remaining message
   */
  message: string;
}

/**
 * Calculate the deadline date/time for a specific meal
 *
 * @param mealDate - The date of the meal
 * @param mealType - The type of meal
 * @param customDeadline - Optional custom deadline config (uses default if not provided)
 * @returns The deadline Date object
 *
 * @example
 * ```typescript
 * // For breakfast on Jan 16, deadline is 10 PM on Jan 15
 * const deadline = calculateMealDeadline(
 *   new Date('2025-01-16'),
 *   MealType.BREAKFAST
 * );
 * // Returns: Date('2025-01-15T22:00:00')
 * ```
 */
export const calculateMealDeadline = (
  mealDate: Date | string,
  mealType: MealType,
  customDeadline?: DeadlineConfig
): Date => {
  const mealDateObj = typeof mealDate === 'string' ? new Date(mealDate) : new Date(mealDate);

  if (isNaN(mealDateObj.getTime())) {
    throw new Error('Invalid meal date provided');
  }

  // Get deadline configuration
  const deadlineConfig = customDeadline || DEFAULT_DEADLINES[mealType];

  // Calculate deadline date
  const deadlineDate = new Date(mealDateObj);

  // Subtract days if needed (e.g., previous day for breakfast)
  if (deadlineConfig.daysBefore > 0) {
    deadlineDate.setDate(deadlineDate.getDate() - deadlineConfig.daysBefore);
  }

  // Set the deadline time
  deadlineDate.setHours(deadlineConfig.hour, deadlineConfig.minute, 0, 0);

  return deadlineDate;
};

/**
 * Check if the deadline for a meal has passed
 *
 * @param mealDate - The date of the meal
 * @param mealType - The type of meal
 * @param currentTime - Current time (defaults to now)
 * @param customDeadline - Optional custom deadline config
 * @returns True if the deadline has passed
 *
 * @example
 * ```typescript
 * // Check if breakfast deadline has passed for Jan 16
 * const hasPassed = checkMealDeadlinePassed(
 *   new Date('2025-01-16'),
 *   MealType.BREAKFAST
 * );
 * ```
 */
export const checkMealDeadlinePassed = (
  mealDate: Date | string,
  mealType: MealType,
  currentTime?: Date,
  customDeadline?: DeadlineConfig
): boolean => {
  const now = currentTime || new Date();
  const deadline = calculateMealDeadline(mealDate, mealType, customDeadline);

  return now > deadline;
};

/**
 * Calculate time remaining until a meal deadline
 *
 * @param mealDate - The date of the meal
 * @param mealType - The type of meal
 * @param currentTime - Current time (defaults to now)
 * @param customDeadline - Optional custom deadline config
 * @returns Time remaining in milliseconds (negative if passed)
 *
 * @example
 * ```typescript
 * const remaining = calculateTimeUntilDeadline(
 *   new Date('2025-01-16'),
 *   MealType.BREAKFAST
 * );
 * // Returns milliseconds until 10 PM on Jan 15
 * ```
 */
export const calculateTimeUntilDeadline = (
  mealDate: Date | string,
  mealType: MealType,
  currentTime?: Date,
  customDeadline?: DeadlineConfig
): number => {
  const now = currentTime || new Date();
  const deadline = calculateMealDeadline(mealDate, mealType, customDeadline);

  return deadline.getTime() - now.getTime();
};

/**
 * Determine if a meal should be locked (cannot be modified)
 *
 * A meal is locked if:
 * 1. The deadline has passed, OR
 * 2. The meal date is in the past
 *
 * @param mealDate - The date of the meal
 * @param mealType - The type of meal
 * @param currentTime - Current time (defaults to now)
 * @param customDeadline - Optional custom deadline config
 * @returns True if the meal should be locked
 *
 * @example
 * ```typescript
 * const isLocked = isMealLocked(
 *   new Date('2025-01-16'),
 *   MealType.BREAKFAST
 * );
 * ```
 */
export const isMealLocked = (
  mealDate: Date | string,
  mealType: MealType,
  currentTime?: Date,
  customDeadline?: DeadlineConfig
): boolean => {
  const now = currentTime || new Date();
  const mealDateObj = typeof mealDate === 'string' ? new Date(mealDate) : new Date(mealDate);

  // Reset time to compare only dates
  const todayStart = new Date(now);
  todayStart.setHours(0, 0, 0, 0);

  const mealDateStart = new Date(mealDateObj);
  mealDateStart.setHours(0, 0, 0, 0);

  // Lock if meal date is in the past
  if (mealDateStart < todayStart) {
    return true;
  }

  // Lock if deadline has passed
  return checkMealDeadlinePassed(mealDate, mealType, now, customDeadline);
};

/**
 * Get comprehensive deadline check result for a meal
 *
 * @param mealDate - The date of the meal
 * @param mealType - The type of meal
 * @param currentTime - Current time (defaults to now)
 * @param customDeadline - Optional custom deadline config
 * @returns Complete deadline check result with all information
 *
 * @example
 * ```typescript
 * const result = checkMealDeadline(
 *   new Date('2025-01-16'),
 *   MealType.BREAKFAST
 * );
 *
 * if (result.isLocked) {
 *   console.log('Cannot modify meal');
 * } else if (result.showWarning) {
 *   console.log(result.message); // "Deadline in 45 minutes"
 * }
 * ```
 */
export const checkMealDeadline = (
  mealDate: Date | string,
  mealType: MealType,
  currentTime?: Date,
  customDeadline?: DeadlineConfig
): DeadlineCheckResult => {
  const now = currentTime || new Date();
  const deadlineDate = calculateMealDeadline(mealDate, mealType, customDeadline);
  const timeRemaining = calculateTimeUntilDeadline(mealDate, mealType, now, customDeadline);

  const isPassed = timeRemaining < 0;
  const isLocked = isMealLocked(mealDate, mealType, now, customDeadline);

  // Check if we should show a warning (deadline approaching)
  const warningThresholdMs = DEADLINE_WARNING_BUFFER_MINUTES * 60 * 1000;
  const showWarning = !isPassed && timeRemaining <= warningThresholdMs;

  // Generate human-readable message
  const message = generateDeadlineMessage(timeRemaining, isPassed, isLocked);

  return {
    isPassed,
    isLocked,
    timeRemaining,
    showWarning,
    deadlineDate,
    message,
  };
};

/**
 * Generate a human-readable message about the deadline
 *
 * @param timeRemaining - Time remaining in milliseconds
 * @param isPassed - Whether the deadline has passed
 * @param isLocked - Whether the meal is locked
 * @returns Human-readable message
 */
const generateDeadlineMessage = (
  timeRemaining: number,
  isPassed: boolean,
  isLocked: boolean
): string => {
  if (isLocked) {
    return 'Meal selection is locked';
  }

  if (isPassed) {
    const timePassed = Math.abs(timeRemaining);
    const hoursAgo = Math.floor(timePassed / (1000 * 60 * 60));
    const minutesAgo = Math.floor((timePassed % (1000 * 60 * 60)) / (1000 * 60));

    if (hoursAgo > 0) {
      return `Deadline passed ${hoursAgo} hour${hoursAgo !== 1 ? 's' : ''} ago`;
    }
    return `Deadline passed ${minutesAgo} minute${minutesAgo !== 1 ? 's' : ''} ago`;
  }

  // Format time remaining
  const hours = Math.floor(timeRemaining / (1000 * 60 * 60));
  const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));

  if (hours > 24) {
    const days = Math.floor(hours / 24);
    return `${days} day${days !== 1 ? 's' : ''} remaining`;
  }

  if (hours > 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''} ${minutes} minute${minutes !== 1 ? 's' : ''} remaining`;
  }

  return `${minutes} minute${minutes !== 1 ? 's' : ''} remaining`;
};

/**
 * Handle dinner previous day deadline check
 * Dinner has a special case where it must be selected before 5 PM on the same day,
 * but if checking for tomorrow's dinner, the deadline is today at 5 PM.
 *
 * @param dinnerDate - The date of the dinner
 * @param currentTime - Current time (defaults to now)
 * @returns Deadline check result
 *
 * @example
 * ```typescript
 * // Checking tomorrow's dinner at 4 PM today
 * const result = checkDinnerDeadline(
 *   new Date('2025-01-16'),
 *   new Date('2025-01-15T16:00:00')
 * );
 * // Result: Not locked, 1 hour remaining
 * ```
 */
export const checkDinnerDeadline = (
  dinnerDate: Date | string,
  currentTime?: Date
): DeadlineCheckResult => {
  // Use the standard deadline check for dinner
  return checkMealDeadline(dinnerDate, MealType.DINNER, currentTime);
};

/**
 * Get the earliest date that can be selected for a meal type
 *
 * @param mealType - The type of meal
 * @param currentTime - Current time (defaults to now)
 * @returns The earliest selectable date
 *
 * @example
 * ```typescript
 * // At 11 PM on Jan 15, earliest breakfast is Jan 17 (deadline for Jan 16 passed)
 * const earliest = getEarliestSelectableDate(MealType.BREAKFAST);
 * ```
 */
export const getEarliestSelectableDate = (
  mealType: MealType,
  currentTime?: Date
): Date => {
  const now = currentTime || new Date();
  let checkDate = new Date(now);
  checkDate.setHours(0, 0, 0, 0);

  // Check if we can still select today's meal
  if (!checkMealDeadlinePassed(checkDate, mealType, now)) {
    return checkDate;
  }

  // Otherwise, return tomorrow
  checkDate.setDate(checkDate.getDate() + 1);
  return checkDate;
};

/**
 * Get all lockable dates for a meal type within a date range
 * Returns dates where the meal cannot be modified
 *
 * @param mealType - The type of meal
 * @param startDate - Start of date range
 * @param endDate - End of date range
 * @param currentTime - Current time (defaults to now)
 * @returns Array of locked dates
 *
 * @example
 * ```typescript
 * const lockedDates = getLockedDates(
 *   MealType.BREAKFAST,
 *   new Date('2025-01-01'),
 *   new Date('2025-01-31')
 * );
 * ```
 */
export const getLockedDates = (
  mealType: MealType,
  startDate: Date | string,
  endDate: Date | string,
  currentTime?: Date
): Date[] => {
  const start = typeof startDate === 'string' ? new Date(startDate) : new Date(startDate);
  const end = typeof endDate === 'string' ? new Date(endDate) : new Date(endDate);
  const now = currentTime || new Date();

  const lockedDates: Date[] = [];
  const currentDate = new Date(start);

  while (currentDate <= end) {
    if (isMealLocked(currentDate, mealType, now)) {
      lockedDates.push(new Date(currentDate));
    }
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return lockedDates;
};

/**
 * Format deadline time for display
 *
 * @param deadlineDate - The deadline date
 * @returns Formatted deadline string
 *
 * @example
 * ```typescript
 * formatDeadlineTime(new Date('2025-01-15T22:00:00'));
 * // Returns: "Jan 15, 2025 at 10:00 PM"
 * ```
 */
export const formatDeadlineTime = (deadlineDate: Date): string => {
  const dateStr = deadlineDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  const timeStr = deadlineDate.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });

  return `${dateStr} at ${timeStr}`;
};
