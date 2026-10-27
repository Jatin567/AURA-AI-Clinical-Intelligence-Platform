/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useEffect } from 'react';
import { useSessionEngine } from './SessionEngine';

const ThemeContext = createContext();

export const ThemeEngineProvider = ({ children }) => {
  const { theme } = useSessionEngine();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useThemeEngine = () => useContext(ThemeContext);
