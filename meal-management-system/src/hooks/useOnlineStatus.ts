import { useState, useEffect } from 'react';

/**
 * Custom hook to detect online/offline status
 * Returns true when online, false when offline
 */
export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      console.log('Connection restored - Back online');
    };

    const handleOffline = () => {
      setIsOnline(false);
      console.log('Connection lost - Now offline');
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Periodic connectivity check (every 30 seconds)
    const checkInterval = setInterval(() => {
      if (navigator.onLine !== isOnline) {
        setIsOnline(navigator.onLine);
      }
    }, 30000);

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(checkInterval);
    };
  }, [isOnline]);

  return isOnline;
};

/**
 * Hook to monitor network information (if available)
 * Returns connection type, effective type, and saveData mode
 */
export const useNetworkInfo = () => {
  const [networkInfo, setNetworkInfo] = useState<{
    effectiveType?: string;
    downlink?: number;
    rtt?: number;
    saveData?: boolean;
  }>({});

  useEffect(() => {
    // Network Information API is not available in all browsers
    const connection = (navigator as any).connection
      || (navigator as any).mozConnection
      || (navigator as any).webkitConnection;

    if (!connection) {
      return;
    }

    const updateNetworkInfo = () => {
      setNetworkInfo({
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData,
      });
    };

    updateNetworkInfo();
    connection.addEventListener('change', updateNetworkInfo);

    return () => {
      connection.removeEventListener('change', updateNetworkInfo);
    };
  }, []);

  return networkInfo;
};

export default useOnlineStatus;
