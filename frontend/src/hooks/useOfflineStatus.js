import { useState, useEffect, useCallback } from 'react';

const useOfflineStatus = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [showBanner, setShowBanner] = useState(false);
  const [swRegistered, setSwRegistered] = useState(false);

  const handleOnline = useCallback(() => {
    setIsOffline(false);
    setShowBanner(true);
    setTimeout(() => setShowBanner(false), 3000);
  }, []);

  const handleOffline = useCallback(() => {
    setIsOffline(true);
    setShowBanner(true);
  }, []);

  useEffect(() => {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/service-worker.js')
        .then((registration) => {
          setSwRegistered(true);
          console.log('SW registered:', registration.scope);
        })
        .catch((err) => {
          console.log('SW registration failed:', err);
        });
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [handleOnline, handleOffline]);

  return { isOffline, showBanner, swRegistered, setShowBanner };
};

export default useOfflineStatus;
