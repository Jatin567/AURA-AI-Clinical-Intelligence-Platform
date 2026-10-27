/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useCallback } from 'react';

const SessionContext = createContext();

export const SessionEngineProvider = ({ children }) => {
  const [conversationState, setConversationState] = useState({ id: null, status: 'idle' });
  const [patientContext, setPatientContext] = useState({});
  const [panelState, setPanelState] = useState({ isOpen: false, view: null });
  const [theme, setTheme] = useState('light');

  const updateConversationStatus = useCallback((status) => {
    setConversationState(prev => ({ ...prev, status }));
  }, []);

  const openPanel = useCallback((view) => {
    setPanelState({ isOpen: true, view });
  }, []);

  const closePanel = useCallback(() => {
    setPanelState(prev => ({ ...prev, isOpen: false }));
  }, []);

  const value = {
    conversationState,
    updateConversationStatus,
    patientContext,
    setPatientContext,
    panelState,
    openPanel,
    closePanel,
    theme,
    setTheme
  };

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
};

export const useSessionEngine = () => useContext(SessionContext);
