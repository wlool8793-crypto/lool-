/**
 * Date utility functions for the Hostel Meal Management System
 * Provides helpers for date formatting, manipulation, and validation
 */

/**
 * Date format options
 */
export type DateFormatOption = 'short' | 'medium' | 'long' | 'full' | 'iso';

/**
 * Format a date to a human-readable string
 *
 * @param date - Date to format (Date object or ISO string)
 * @param format - Format option (default: 'medium')
 * @returns Formatted date string
 *
 * @example
 * ```typescript
 * formatDate(new Date('2025-01-15'), 'short');  // "15/01/2025"
 * formatDate(new Date('2025-01-15'), 'medium'); // "Jan 15, 2025"
 * formatDate(new Date('2025-01-15'), 'long');   // "January 15, 2025"
 * formatDate(new Date('2025-01-15'), 'full');   // "Wednesday, January 15, 2025"
 * formatDate(new Date('2025-01-15'), 'iso');    // "2025-01-15"
 * ```
 */
export const formatDate = (
  date: Date | string,
  format: DateFormatOption = 'medium'
): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    throw new Error('Invalid date provided');
  }

  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });

    case 'medium':
      return dateObj.toLocaleDateString('en-US', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });

    case 'long':
      return dateObj.toLocaleDateString('en-US', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });

    case 'full':
      return dateObj.toLocaleDateString('en-US', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });

    case 'iso':
      return dateObj.toISOString().split('T')[0];

    default:
      return dateObj.toLocaleDateString('en-US');
  }
};

/**
 * Get month string in YYYY-MM format
 *
 * @param date - Date object or ISO string (defaults to current date)
 * @returns Month string in YYYY-MM format
 *
 * @example
 * ```typescript
 * getMonthString(new Date('2025-01-15')); // "2025-01"
 * getMonthString(); // Current month like "2025-10"
 * ```
 */
export const getMonthString = (date?: Date | string): string => {
  const dateObj = date
    ? typeof date === 'string'
      ? new Date(date)
      : date
    : new Date();

  if (isNaN(dateObj.getTime())) {
    throw new Error('Invalid date provided');
  }

  const year = dateObj.getFullYear();
  const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');

  return `${year}-${month}`;
};

/**
 * Get human-readable month name and year
 *
 * @param monthString - Month string in YYYY-MM format
 * @returns Formatted month and year (e.g., "January 2025")
 *
 * @example
 * ```typescript
 * getMonthName('2025-01'); // "January 2025"
 * ```
 */
export const getMonthName = (monthString: string): string => {
  const [year, month] = monthString.split('-');
  const date = new Date(parseInt(year), parseInt(month) - 1, 1);

  return date.toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  });
};

/**
 * Check if a date is in the past
 *
 * @param date - Date to check (Date object or ISO string)
 * @param includeToday - Whether to consider today as past (default: false)
 * @returns True if date is in the past
 *
 * @example
 * ```typescript
 * isDateInPast(new Date('2024-01-01')); // true
 * isDateInPast(new Date()); // false
 * isDateInPast(new Date(), true); // true
 * ```
 */
export const isDateInPast = (
  date: Date | string,
  includeToday: boolean = false
): boolean => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();

  // Reset time to compare only dates
  dateObj.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  if (includeToday) {
    return dateObj <= today;
  }

  return dateObj < today;
};

/**
 * Check if a date is today
 *
 * @param date - Date to check (Date object or ISO string)
 * @returns True if date is today
 *
 * @example
 * ```typescript
 * isToday(new Date()); // true
 * isToday(new Date('2024-01-01')); // false
 * ```
 */
export const isToday = (date: Date | string): boolean => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();

  return (
    dateObj.getDate() === today.getDate() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getFullYear() === today.getFullYear()
  );
};

/**
 * Check if a date is in the future
 *
 * @param date - Date to check (Date object or ISO string)
 * @returns True if date is in the future
 */
export const isDateInFuture = (date: Date | string): boolean => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();

  // Reset time to compare only dates
  dateObj.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  return dateObj > today;
};

/**
 * Generate an array of dates for a date range
 *
 * @param startDate - Start date of the range
 * @param endDate - End date of the range
 * @returns Array of Date objects for each day in the range
 *
 * @example
 * ```typescript
 * const dates = generateDateRange(
 *   new Date('2025-01-01'),
 *   new Date('2025-01-05')
 * );
 * // Returns 5 dates from Jan 1 to Jan 5
 * ```
 */
export const generateDateRange = (
  startDate: Date | string,
  endDate: Date | string
): Date[] => {
  const start = typeof startDate === 'string' ? new Date(startDate) : new Date(startDate);
  const end = typeof endDate === 'string' ? new Date(endDate) : new Date(endDate);

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    throw new Error('Invalid date range provided');
  }

  if (start > end) {
    throw new Error('Start date must be before or equal to end date');
  }

  const dates: Date[] = [];
  const currentDate = new Date(start);

  while (currentDate <= end) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return dates;
};

/**
 * Generate date range for a specific month
 *
 * @param year - Year
 * @param month - Month (1-12)
 * @returns Array of Date objects for each day in the month
 *
 * @example
 * ```typescript
 * const dates = generateMonthDateRange(2025, 1);
 * // Returns all dates in January 2025
 * ```
 */
export const generateMonthDateRange = (year: number, month: number): Date[] => {
  if (month < 1 || month > 12) {
    throw new Error('Month must be between 1 and 12');
  }

  const startDate = new Date(year, month - 1, 1);
  const endDate = new Date(year, month, 0); // Last day of the month

  return generateDateRange(startDate, endDate);
};

/**
 * Get the number of days in a month
 *
 * @param year - Year
 * @param month - Month (1-12)
 * @returns Number of days in the month
 *
 * @example
 * ```typescript
 * getDaysInMonth(2025, 1); // 31
 * getDaysInMonth(2025, 2); // 28
 * getDaysInMonth(2024, 2); // 29 (leap year)
 * ```
 */
export const getDaysInMonth = (year: number, month: number): number => {
  if (month < 1 || month > 12) {
    throw new Error('Month must be between 1 and 12');
  }

  return new Date(year, month, 0).getDate();
};

/**
 * Add days to a date
 *
 * @param date - Starting date
 * @param days - Number of days to add (can be negative)
 * @returns New date with days added
 *
 * @example
 * ```typescript
 * addDays(new Date('2025-01-15'), 5); // Jan 20, 2025
 * addDays(new Date('2025-01-15'), -5); // Jan 10, 2025
 * ```
 */
export const addDays = (date: Date | string, days: number): Date => {
  const dateObj = typeof date === 'string' ? new Date(date) : new Date(date);

  if (isNaN(dateObj.getTime())) {
    throw new Error('Invalid date provided');
  }

  const result = new Date(dateObj);
  result.setDate(result.getDate() + days);
  return result;
};

/**
 * Get the difference in days between two dates
 *
 * @param date1 - First date
 * @param date2 - Second date
 * @returns Number of days between the dates (can be negative)
 *
 * @example
 * ```typescript
 * getDaysDifference(
 *   new Date('2025-01-20'),
 *   new Date('2025-01-15')
 * ); // 5
 * ```
 */
export const getDaysDifference = (
  date1: Date | string,
  date2: Date | string
): number => {
  const d1 = typeof date1 === 'string' ? new Date(date1) : new Date(date1);
  const d2 = typeof date2 === 'string' ? new Date(date2) : new Date(date2);

  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) {
    throw new Error('Invalid date provided');
  }

  // Reset time to compare only dates
  d1.setHours(0, 0, 0, 0);
  d2.setHours(0, 0, 0, 0);

  const diffTime = d1.getTime() - d2.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  return diffDays;
};

/**
 * Get the day of the week
 *
 * @param date - Date to check
 * @returns Day name (e.g., "Monday", "Tuesday")
 *
 * @example
 * ```typescript
 * getDayOfWeek(new Date('2025-01-15')); // "Wednesday"
 * ```
 */
export const getDayOfWeek = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    throw new Error('Invalid date provided');
  }

  return dateObj.toLocaleDateString('en-US', { weekday: 'long' });
};

/**
 * Get calendar data for a specific month (including padding days)
 *
 * @param year - Year
 * @param month - Month (1-12)
 * @returns Array of weeks, each containing 7 days (may include null for padding)
 *
 * @example
 * ```typescript
 * const calendar = getCalendarMonth(2025, 1);
 * // Returns calendar grid for January 2025
 * ```
 */
export const getCalendarMonth = (
  year: number,
  month: number
): Array<Array<Date | null>> => {
  if (month < 1 || month > 12) {
    throw new Error('Month must be between 1 and 12');
  }

  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);

  const startPadding = firstDay.getDay(); // 0 = Sunday, 6 = Saturday
  const endPadding = 6 - lastDay.getDay();

  const calendar: Array<Array<Date | null>> = [];
  let week: Array<Date | null> = [];

  // Add padding at the start
  for (let i = 0; i < startPadding; i++) {
    week.push(null);
  }

  // Add all days of the month
  const daysInMonth = getDaysInMonth(year, month);
  for (let day = 1; day <= daysInMonth; day++) {
    week.push(new Date(year, month - 1, day));

    if (week.length === 7) {
      calendar.push(week);
      week = [];
    }
  }

  // Add padding at the end
  if (week.length > 0) {
    for (let i = week.length; i < 7; i++) {
      week.push(null);
    }
    calendar.push(week);
  }

  return calendar;
};

/**
 * Parse month string to year and month numbers
 *
 * @param monthString - Month string in YYYY-MM format
 * @returns Object with year and month numbers
 *
 * @example
 * ```typescript
 * parseMonthString('2025-01'); // { year: 2025, month: 1 }
 * ```
 */
export const parseMonthString = (
  monthString: string
): { year: number; month: number } => {
  const [year, month] = monthString.split('-').map(Number);

  if (!year || !month || month < 1 || month > 12) {
    throw new Error('Invalid month string format. Expected YYYY-MM');
  }

  return { year, month };
};
