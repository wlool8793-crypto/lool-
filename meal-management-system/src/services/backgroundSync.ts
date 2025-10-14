/**
 * Background Sync Service
 * Handles offline meal updates and syncs them when connection is restored
 */

interface PendingMealUpdate {
  id: string;
  type: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
}

const STORAGE_KEY = 'pending-meal-updates';
const SYNC_TAG = 'meal-sync';

/**
 * Get all pending updates from localStorage
 */
export const getPendingUpdates = (): PendingMealUpdate[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error reading pending updates:', error);
    return [];
  }
};

/**
 * Save pending updates to localStorage
 */
const savePendingUpdates = (updates: PendingMealUpdate[]): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updates));
  } catch (error) {
    console.error('Error saving pending updates:', error);
  }
};

/**
 * Add a new pending update
 */
export const addPendingUpdate = (
  type: PendingMealUpdate['type'],
  data: any
): string => {
  const updates = getPendingUpdates();
  const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  const newUpdate: PendingMealUpdate = {
    id,
    type,
    data,
    timestamp: Date.now(),
  };

  updates.push(newUpdate);
  savePendingUpdates(updates);

  // Request background sync if available
  requestBackgroundSync();

  console.log(`Added pending ${type} update:`, id);
  return id;
};

/**
 * Remove a processed update
 */
export const removePendingUpdate = (id: string): void => {
  const updates = getPendingUpdates();
  const filtered = updates.filter((update) => update.id !== id);
  savePendingUpdates(filtered);
};

/**
 * Clear all pending updates
 */
export const clearPendingUpdates = (): void => {
  localStorage.removeItem(STORAGE_KEY);
};

/**
 * Get count of pending updates
 */
export const getPendingCount = (): number => {
  return getPendingUpdates().length;
};

/**
 * Request background sync (if supported)
 */
export const requestBackgroundSync = async (): Promise<void> => {
  if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync?.register(SYNC_TAG);
      console.log('Background sync registered');
    } catch (error) {
      console.log('Background sync registration failed:', error);
      // Fallback: try to sync immediately
      syncPendingUpdates();
    }
  } else {
    // Fallback: try to sync immediately
    console.log('Background sync not supported, syncing immediately');
    syncPendingUpdates();
  }
};

/**
 * Process all pending updates
 */
export const syncPendingUpdates = async (): Promise<{
  success: number;
  failed: number;
}> => {
  const updates = getPendingUpdates();

  if (updates.length === 0) {
    return { success: 0, failed: 0 };
  }

  console.log(`Syncing ${updates.length} pending updates...`);

  let successCount = 0;
  let failedCount = 0;

  for (const update of updates) {
    try {
      // Process the update based on type
      const success = await processUpdate(update);

      if (success) {
        removePendingUpdate(update.id);
        successCount++;
      } else {
        failedCount++;
      }
    } catch (error) {
      console.error('Error processing update:', error);
      failedCount++;
    }
  }

  console.log(`Sync complete: ${successCount} success, ${failedCount} failed`);

  return { success: successCount, failed: failedCount };
};

/**
 * Process a single update
 */
const processUpdate = async (update: PendingMealUpdate): Promise<boolean> => {
  try {
    // Import supabase dynamically to avoid circular dependencies
    const { supabase } = await import('./supabase');

    switch (update.type) {
      case 'create':
        const { error: createError } = await supabase
          .from(update.data.table)
          .insert(update.data.values);

        if (createError) throw createError;
        return true;

      case 'update':
        const { error: updateError } = await supabase
          .from(update.data.table)
          .update(update.data.values)
          .eq('id', update.data.id);

        if (updateError) throw updateError;
        return true;

      case 'delete':
        const { error: deleteError } = await supabase
          .from(update.data.table)
          .delete()
          .eq('id', update.data.id);

        if (deleteError) throw deleteError;
        return true;

      default:
        console.error('Unknown update type:', update.type);
        return false;
    }
  } catch (error) {
    console.error('Error processing update:', error);
    return false;
  }
};

/**
 * Initialize background sync listeners
 */
export const initBackgroundSync = (): void => {
  // Listen for online event to trigger sync
  window.addEventListener('online', () => {
    console.log('Connection restored, syncing pending updates...');
    syncPendingUpdates();
  });

  // Check for pending updates on page load
  if (navigator.onLine) {
    const pendingCount = getPendingCount();
    if (pendingCount > 0) {
      console.log(`Found ${pendingCount} pending updates, syncing...`);
      syncPendingUpdates();
    }
  }

  // Register service worker sync event handler
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      console.log('Service worker ready for background sync');
    });
  }
};

/**
 * Export utility functions
 */
export default {
  getPendingUpdates,
  addPendingUpdate,
  removePendingUpdate,
  clearPendingUpdates,
  getPendingCount,
  syncPendingUpdates,
  requestBackgroundSync,
  initBackgroundSync,
};
