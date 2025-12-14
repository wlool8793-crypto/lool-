import React from 'react';
import { RefreshCw, CheckCircle, AlertCircle, WifiOff } from 'lucide-react';
import { usePWA } from '../../contexts/PWAContext';

const SyncStatus: React.FC = () => {
  const { isOffline, pendingUpdatesCount, syncNow } = usePWA();

  if (!isOffline && pendingUpdatesCount === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-20 right-4 z-40 max-w-sm">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            {isOffline ? (
              <WifiOff className="w-5 h-5 text-red-500" />
            ) : (
              <RefreshCw className="w-5 h-5 text-blue-500" />
            )}
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Sync Status
            </h3>
          </div>
        </div>

        {/* Status Info */}
        <div className="space-y-2 mb-4">
          {isOffline ? (
            <div className="flex items-start space-x-2 text-sm">
              <AlertCircle className="w-4 h-4 text-orange-500 mt-0.5" />
              <p className="text-gray-600 dark:text-gray-400">
                You're offline. Updates will sync when connection is restored.
              </p>
            </div>
          ) : (
            <div className="flex items-start space-x-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
              <p className="text-gray-600 dark:text-gray-400">
                Connected and ready to sync
              </p>
            </div>
          )}

          {pendingUpdatesCount > 0 && (
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded p-2 text-sm">
              <p className="text-blue-900 dark:text-blue-300">
                <strong>{pendingUpdatesCount}</strong> pending update
                {pendingUpdatesCount !== 1 ? 's' : ''}
              </p>
            </div>
          )}
        </div>

        {/* Action Button */}
        {!isOffline && pendingUpdatesCount > 0 && (
          <button
            onClick={syncNow}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Sync Now</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default SyncStatus;
