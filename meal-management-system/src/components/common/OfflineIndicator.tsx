import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi } from 'lucide-react';
import { useOnlineStatus } from '../../hooks/useOnlineStatus';

const OfflineIndicator: React.FC = () => {
  const isOnline = useOnlineStatus();
  const [showNotification, setShowNotification] = useState(false);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      // Show offline notification
      setShowNotification(true);
      setWasOffline(true);
    } else if (wasOffline) {
      // Show back online notification briefly
      setShowNotification(true);
      const timer = setTimeout(() => {
        setShowNotification(false);
        setWasOffline(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, wasOffline]);

  if (!showNotification) {
    return null;
  }

  return (
    <>
      {/* Fixed position banner */}
      <div
        className={`fixed top-0 left-0 right-0 z-50 transform transition-all duration-500 ease-in-out ${
          showNotification ? 'translate-y-0' : '-translate-y-full'
        }`}
      >
        <div
          className={`${
            isOnline
              ? 'bg-green-500'
              : 'bg-red-500'
          } text-white px-4 py-3 shadow-lg`}
        >
          <div className="container mx-auto flex items-center justify-center space-x-3">
            {isOnline ? (
              <>
                <Wifi className="w-5 h-5" />
                <span className="font-medium">Back online - Changes will sync automatically</span>
              </>
            ) : (
              <>
                <WifiOff className="w-5 h-5" />
                <span className="font-medium">You're offline - Some features may be limited</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Floating indicator (always visible when offline) */}
      {!isOnline && (
        <div className="fixed bottom-4 right-4 z-40 animate-bounce">
          <div className="bg-red-500 text-white px-4 py-2 rounded-full shadow-lg flex items-center space-x-2">
            <WifiOff className="w-4 h-4" />
            <span className="text-sm font-medium">Offline</span>
          </div>
        </div>
      )}
    </>
  );
};

export default OfflineIndicator;
