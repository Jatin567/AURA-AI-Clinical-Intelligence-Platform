/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useCallback } from 'react';
import { useSessionEngine } from './SessionEngine';
import { useNavigate } from 'react-router-dom';

const InteractionContext = createContext();

export const InteractionEngineProvider = ({ children }) => {
  const { openPanel } = useSessionEngine();
  const navigate = useNavigate();

  const handleAction = useCallback((action) => {
    switch(action.action_type) {
      case 'navigate':
        navigate(action.payload.path);
        break;
      case 'open_panel':
        openPanel(action.payload.view);
        break;
      case 'open_modal':
        // Stub for modal
        console.log('Open modal:', action.payload);
        break;
      case 'download':
      case 'copy':
      case 'retry':
      case 'trigger_tool':
      case 'api_call':
        console.log(`Action handled: ${action.action_type}`, action.payload);
        break;
      default:
        console.warn(`Unknown action type: ${action.action_type}`);
    }
  }, [navigate, openPanel]);

  return (
    <InteractionContext.Provider value={{ handleAction }}>
      {children}
    </InteractionContext.Provider>
  );
};

export const useInteractionEngine = () => useContext(InteractionContext);
