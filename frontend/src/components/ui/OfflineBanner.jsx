import React from 'react';
import useOfflineStatus from '../../hooks/useOfflineStatus';

const OfflineBanner = () => {
  const { isOffline, showBanner, setShowBanner } = useOfflineStatus();

  if (!showBanner && !isOffline) return null;

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-50 transition-transform duration-300 ${
        isOffline || showBanner ? 'translate-y-0' : '-translate-y-full'
      }`}
      data-testid="offline-banner"
    >
      {isOffline ? (
        <div className="bg-amber-500 text-white px-4 py-2 text-center text-sm font-medium flex items-center justify-center gap-2">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414" />
          </svg>
          <span>Mode hors ligne - Les donnees affichees proviennent du cache</span>
        </div>
      ) : (
        <div className="bg-emerald-500 text-white px-4 py-2 text-center text-sm font-medium flex items-center justify-center gap-2">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>Connexion retablie</span>
          <button onClick={() => setShowBanner(false)} className="ml-2 underline text-xs">Fermer</button>
        </div>
      )}
    </div>
  );
};

export default OfflineBanner;
