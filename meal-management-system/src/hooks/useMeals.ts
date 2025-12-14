import { useState, useCallback, useEffect } from 'react';
import { Meal, InsertMeal } from '../types/database.types';
import * as mealsService from '../services/meals.service';
import toast from 'react-hot-toast';

interface UseMealsOptions {
  userId?: string;
  mealDate?: string;
  startDate?: string;
  endDate?: string;
  autoFetch?: boolean;
}

interface UseMealsReturn {
  meals: Meal[];
  currentMeal: Meal | null;
  loading: boolean;
  error: string | null;
  fetchMeals: () => Promise<void>;
  fetchMealByDate: (date: string) => Promise<void>;
  createOrUpdateMeal: (meal: InsertMeal) => Promise<boolean>;
  updateMealById: (id: string, updates: Partial<Omit<Meal, 'id' | 'created_at'>>) => Promise<boolean>;
  deleteMeal: (id: string) => Promise<boolean>;
  checkIfLocked: (mealDate: string, mealType: 'breakfast' | 'lunch' | 'dinner') => Promise<boolean>;
  refreshMeals: () => Promise<void>;
}

/**
 * Custom hook for meal operations
 */
export const useMeals = (options: UseMealsOptions = {}): UseMealsReturn => {
  const { userId, mealDate, startDate, endDate, autoFetch = true } = options;

  const [meals, setMeals] = useState<Meal[]>([]);
  const [currentMeal, setCurrentMeal] = useState<Meal | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch meals for a user
  const fetchMeals = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await mealsService.getMealsByUser(userId, startDate, endDate);

      if (response.success && response.data) {
        setMeals(response.data);
      } else {
        setError(response.error || 'Failed to fetch meals');
        toast.error(response.error || 'Failed to fetch meals');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [userId, startDate, endDate]);

  // Fetch a specific meal by date
  const fetchMealByDate = useCallback(
    async (date: string) => {
      if (!userId) return;

      setLoading(true);
      setError(null);

      try {
        const response = await mealsService.getMealByUserAndDate(userId, date);

        if (response.success) {
          setCurrentMeal(response.data);
        } else {
          setError(response.error || 'Failed to fetch meal');
          toast.error(response.error || 'Failed to fetch meal');
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
        setError(errorMessage);
        toast.error(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  // Create or update a meal (upsert)
  const createOrUpdateMeal = useCallback(async (meal: InsertMeal): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const response = await mealsService.upsertMeal(meal);

      if (response.success && response.data) {
        toast.success('Meal updated successfully');
        setCurrentMeal(response.data);
        return true;
      } else {
        setError(response.error || 'Failed to update meal');
        toast.error(response.error || 'Failed to update meal');
        return false;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update a meal by ID
  const updateMealById = useCallback(
    async (id: string, updates: Partial<Omit<Meal, 'id' | 'created_at'>>): Promise<boolean> => {
      setLoading(true);
      setError(null);

      try {
        const response = await mealsService.updateMeal(id, updates);

        if (response.success && response.data) {
          toast.success('Meal updated successfully');
          setCurrentMeal(response.data);
          return true;
        } else {
          setError(response.error || 'Failed to update meal');
          toast.error(response.error || 'Failed to update meal');
          return false;
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
        setError(errorMessage);
        toast.error(errorMessage);
        return false;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // Delete a meal
  const deleteMeal = useCallback(async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const response = await mealsService.deleteMeal(id);

      if (response.success) {
        toast.success('Meal deleted successfully');
        setCurrentMeal(null);
        return true;
      } else {
        setError(response.error || 'Failed to delete meal');
        toast.error(response.error || 'Failed to delete meal');
        return false;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Check if a meal type is locked
  const checkIfLocked = useCallback(
    async (date: string, mealType: 'breakfast' | 'lunch' | 'dinner'): Promise<boolean> => {
      if (!userId) return false;

      try {
        const response = await mealsService.isMealLocked(userId, date, mealType);
        return response.success && response.data ? response.data : false;
      } catch (err) {
        console.error('Error checking meal lock status:', err);
        return false;
      }
    },
    [userId]
  );

  // Refresh meals
  const refreshMeals = useCallback(async () => {
    await fetchMeals();
    if (mealDate) {
      await fetchMealByDate(mealDate);
    }
  }, [fetchMeals, fetchMealByDate, mealDate]);

  // Auto-fetch on mount and when dependencies change
  useEffect(() => {
    if (autoFetch) {
      if (userId && mealDate) {
        fetchMealByDate(mealDate);
      } else if (userId) {
        fetchMeals();
      }
    }
  }, [autoFetch, userId, mealDate, fetchMeals, fetchMealByDate]);

  return {
    meals,
    currentMeal,
    loading,
    error,
    fetchMeals,
    fetchMealByDate,
    createOrUpdateMeal,
    updateMealById,
    deleteMeal,
    checkIfLocked,
    refreshMeals,
  };
};
