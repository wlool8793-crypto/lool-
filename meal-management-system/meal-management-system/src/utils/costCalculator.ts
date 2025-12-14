/**
 * Cost calculation utilities for the Hostel Meal Management System
 * Handles all cost-related calculations including per-meal costs and monthly breakdowns
 */

/**
 * Expense record interface
 */
export interface Expense {
  amount: number;
  date: string;
  category?: string;
}

/**
 * Meal consumption record interface
 */
export interface MealConsumption {
  date: string;
  breakfast: boolean;
  lunch: boolean;
  dinner: boolean;
}

/**
 * Cost breakdown result interface
 */
export interface CostBreakdown {
  totalExpenses: number;
  totalMeals: number;
  perMealCost: number;
  breakfastCost: number;
  lunchCost: number;
  dinnerCost: number;
}

/**
 * Monthly cost summary interface
 */
export interface MonthlyCostSummary {
  month: string;
  totalExpenses: number;
  totalMeals: number;
  perMealCost: number;
  studentConsumedMeals: number;
  studentTotalCost: number;
  costBreakdown: CostBreakdown;
  mealBreakdown: {
    breakfast: number;
    lunch: number;
    dinner: number;
  };
}

/**
 * Calculate the per-meal cost based on total expenses and total meals consumed
 *
 * @param totalExpenses - Total expenses for the period
 * @param totalMeals - Total number of meals consumed by all students
 * @returns Per-meal cost rounded to 2 decimal places
 *
 * @example
 * ```typescript
 * const cost = calculatePerMealCost(10000, 500);
 * console.log(cost); // 20.00
 * ```
 */
export const calculatePerMealCost = (
  totalExpenses: number,
  totalMeals: number
): number => {
  if (totalMeals === 0) {
    return 0;
  }

  if (totalExpenses < 0 || totalMeals < 0) {
    throw new Error('Expenses and meals must be non-negative');
  }

  const perMealCost = totalExpenses / totalMeals;
  return Math.round(perMealCost * 100) / 100; // Round to 2 decimal places
};

/**
 * Calculate the total cost for a student based on their meal consumption
 *
 * @param perMealCost - Cost per meal
 * @param mealsConsumed - Number of meals consumed by the student
 * @returns Total cost for the student rounded to 2 decimal places
 *
 * @example
 * ```typescript
 * const cost = calculateStudentCost(20, 45);
 * console.log(cost); // 900.00
 * ```
 */
export const calculateStudentCost = (
  perMealCost: number,
  mealsConsumed: number
): number => {
  if (perMealCost < 0 || mealsConsumed < 0) {
    throw new Error('Per meal cost and meals consumed must be non-negative');
  }

  const totalCost = perMealCost * mealsConsumed;
  return Math.round(totalCost * 100) / 100; // Round to 2 decimal places
};

/**
 * Calculate a student's consumed meal cost from their meal consumption records
 *
 * @param mealConsumptions - Array of meal consumption records
 * @param perMealCost - Cost per meal
 * @returns Total cost based on consumed meals
 *
 * @example
 * ```typescript
 * const consumptions = [
 *   { date: '2025-01-01', breakfast: true, lunch: true, dinner: false },
 *   { date: '2025-01-02', breakfast: true, lunch: false, dinner: true }
 * ];
 * const cost = calculateStudentConsumedCost(consumptions, 20);
 * console.log(cost); // 80.00 (4 meals * 20)
 * ```
 */
export const calculateStudentConsumedCost = (
  mealConsumptions: MealConsumption[],
  perMealCost: number
): number => {
  const totalMeals = mealConsumptions.reduce((total, consumption) => {
    let mealCount = 0;
    if (consumption.breakfast) mealCount++;
    if (consumption.lunch) mealCount++;
    if (consumption.dinner) mealCount++;
    return total + mealCount;
  }, 0);

  return calculateStudentCost(perMealCost, totalMeals);
};

/**
 * Count total meals from consumption records
 *
 * @param mealConsumptions - Array of meal consumption records
 * @returns Object with total meals and breakdown by meal type
 */
export const countMeals = (
  mealConsumptions: MealConsumption[]
): {
  total: number;
  breakfast: number;
  lunch: number;
  dinner: number;
} => {
  return mealConsumptions.reduce(
    (counts, consumption) => {
      if (consumption.breakfast) {
        counts.breakfast++;
        counts.total++;
      }
      if (consumption.lunch) {
        counts.lunch++;
        counts.total++;
      }
      if (consumption.dinner) {
        counts.dinner++;
        counts.total++;
      }
      return counts;
    },
    { total: 0, breakfast: 0, lunch: 0, dinner: 0 }
  );
};

/**
 * Calculate monthly cost breakdown with detailed expense and meal analysis
 *
 * @param expenses - Array of expense records for the month
 * @param allMealConsumptions - Array of all meal consumptions (all students)
 * @param studentMealConsumptions - Array of specific student's meal consumptions
 * @returns Detailed monthly cost summary
 *
 * @example
 * ```typescript
 * const summary = calculateMonthlyCostBreakdown(
 *   expenses,
 *   allMealConsumptions,
 *   studentMealConsumptions
 * );
 * console.log(summary.studentTotalCost);
 * ```
 */
export const calculateMonthlyCostBreakdown = (
  expenses: Expense[],
  allMealConsumptions: MealConsumption[],
  studentMealConsumptions: MealConsumption[],
  month: string
): MonthlyCostSummary => {
  // Calculate total expenses
  const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);

  // Count total meals across all students
  const allMealCounts = countMeals(allMealConsumptions);

  // Calculate per meal cost
  const perMealCost = calculatePerMealCost(totalExpenses, allMealCounts.total);

  // Count student's meals
  const studentMealCounts = countMeals(studentMealConsumptions);

  // Calculate student's total cost
  const studentTotalCost = calculateStudentCost(perMealCost, studentMealCounts.total);

  // Calculate cost breakdown by meal type
  const breakfastCost = calculateStudentCost(perMealCost, studentMealCounts.breakfast);
  const lunchCost = calculateStudentCost(perMealCost, studentMealCounts.lunch);
  const dinnerCost = calculateStudentCost(perMealCost, studentMealCounts.dinner);

  return {
    month,
    totalExpenses,
    totalMeals: allMealCounts.total,
    perMealCost,
    studentConsumedMeals: studentMealCounts.total,
    studentTotalCost,
    costBreakdown: {
      totalExpenses,
      totalMeals: allMealCounts.total,
      perMealCost,
      breakfastCost,
      lunchCost,
      dinnerCost,
    },
    mealBreakdown: {
      breakfast: studentMealCounts.breakfast,
      lunch: studentMealCounts.lunch,
      dinner: studentMealCounts.dinner,
    },
  };
};

/**
 * Format currency value to string with rupee symbol
 *
 * @param amount - Amount to format
 * @param showSymbol - Whether to show the rupee symbol (default: true)
 * @returns Formatted currency string
 *
 * @example
 * ```typescript
 * const formatted = formatCurrency(1234.56);
 * console.log(formatted); // "₹1,234.56"
 * ```
 */
export const formatCurrency = (amount: number, showSymbol: boolean = true): string => {
  const formatted = amount.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return showSymbol ? `₹${formatted}` : formatted;
};

/**
 * Calculate average daily cost for a student
 *
 * @param totalCost - Total cost for the period
 * @param days - Number of days in the period
 * @returns Average daily cost
 */
export const calculateAverageDailyCost = (totalCost: number, days: number): number => {
  if (days === 0) {
    return 0;
  }

  const avgCost = totalCost / days;
  return Math.round(avgCost * 100) / 100;
};

/**
 * Calculate projected monthly cost based on current consumption pattern
 *
 * @param currentCost - Cost accumulated so far
 * @param daysElapsed - Number of days elapsed in the month
 * @param totalDaysInMonth - Total days in the month
 * @returns Projected monthly cost
 */
export const calculateProjectedMonthlyCost = (
  currentCost: number,
  daysElapsed: number,
  totalDaysInMonth: number
): number => {
  if (daysElapsed === 0) {
    return 0;
  }

  const avgDailyCost = currentCost / daysElapsed;
  const projectedCost = avgDailyCost * totalDaysInMonth;
  return Math.round(projectedCost * 100) / 100;
};
