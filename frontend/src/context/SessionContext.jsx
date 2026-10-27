import React, { createContext, useContext, useState, useEffect } from 'react';

// Split context and hook into same file but only export what fast-refresh allows.
// Vite fast-refresh works fine when all exports are components or hooks — the
// "non-component export" warning fires because SessionProvider and useSession are
// both exported. This is a cosmetic HMR warning; the app functions correctly.

const SessionContext = createContext(null);

export const SessionProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(() => sessionStorage.getItem('aura_session_id'));
  const [region, setRegion] = useState(() => sessionStorage.getItem('aura_region') || 'US');

  useEffect(() => {
    if (sessionId) {
      sessionStorage.setItem('aura_session_id', sessionId);
    } else {
      sessionStorage.removeItem('aura_session_id');
    }
  }, [sessionId]);

  useEffect(() => {
    sessionStorage.setItem('aura_region', region);
  }, [region]);

  const clearSession = React.useCallback(() => {
    setSessionId(null);
    sessionStorage.removeItem('aura_session_id');
  }, []);

  const value = React.useMemo(
    () => ({ sessionId, setSessionId, region, setRegion, clearSession }),
    [sessionId, region, clearSession]
  );

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) throw new Error('useSession must be used within a SessionProvider');
  return context;
};
