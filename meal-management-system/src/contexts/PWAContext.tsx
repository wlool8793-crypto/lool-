import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRegisterSW } from 'virtual:pwa-register/react';
import { initBackgroundSync, getPendingCount, syncPendingUpdates } from '../services/backgroundSync';
import toast from 'react-hot-toast';

interface PWAContextType {
  isUpdateAvailable: boolean;
  updateServiceWorker: () => void;
  isOffline: boolean;
  pendingUpdatesCount: number;
  syncNow: () => Promise<void>;
}

const PWAContext = createContext<PWAContextType | undefined>(undefined);

export const usePWA = () => {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWA must be used within PWAProvider');
  }
  return context;
};

export const PWAProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [pendingUpdatesCount, setPendingUpdatesCount] = useState(0);

  // Register service worker and handle updates
  const {
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegistered(registration) {
      console.log('Service Worker registered:', registration);
    },
    onRegisterError(error) {
      console.error('Service Worker registration error:', error);
    },
    onNeedRefresh() {
      toast((t) => (
        <div className="flex flex-col space-y-2">
          <span className="font-semibold">New version available!</span>
          <div className="flex space-x-2">
            <button
              onClick={() => {
                updateServiceWorker(true);
                toast.dismiss(t.id);
              }}
              className="bg-indigo-600 text-white px-3 py-1 rounded text-sm"
            >
              Update
            </button>
            <button
              onClick={() => toast.dismiss(t.id)}
              className="bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm"
            >
              Later
            </button>
          </div>
        </div>
      ), {
        duration: Infinity,
        position: 'bottom-center',
      });
    },
    onOfflineReady() {
      console.log('App ready to work offline');
      toast.success('App is ready to work offline', {
        icon: '✓',
      });
    },
  });

  // Initialize background sync
  useEffect(() => {
    initBackgroundSync();
  }, []);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      toast.success('Back online!', {
        icon: '🌐',
        duration: 3000,
      });
    };

    const handleOffline = () => {
      setIsOffline(true);
      toast.error('You are offline', {
        icon: '📡',
        duration: 5000,
      });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Update pending updates count
  useEffect(() => {
    const updateCount = () => {
      setPendingUpdatesCount(getPendingCount());
    };

    updateCount();

    // Update count every 10 seconds
    const interval = setInterval(updateCount, 10000);

    return () => clearInterval(interval);
  }, []);

  const syncNow = async () => {
    try {
      toast.loading('Syncing updates...', { id: 'sync' });
      const result = await syncPendingUpdates();

      if (result.success > 0) {
        toast.success(`Synced ${result.success} updates`, { id: 'sync' });
        setPendingUpdatesCount(getPendingCount());
      } else if (result.failed > 0) {
        toast.error(`Failed to sync ${result.failed} updates`, { id: 'sync' });
      } else {
        toast.success('All updates are synced', { id: 'sync' });
      }
    } catch (error) {
      toast.error('Sync failed', { id: 'sync' });
    }
  };

  const value: PWAContextType = {
    isUpdateAvailable: needRefresh,
    updateServiceWorker: () => updateServiceWorker(true),
    isOffline,
    pendingUpdatesCount,
    syncNow,
  };

  return <PWAContext.Provider value={value}>{children}</PWAContext.Provider>;
};

export default PWAContext;
