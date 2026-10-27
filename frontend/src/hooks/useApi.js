import { useCallback, useMemo } from 'react';
import { useSession } from '../context/SessionContext';

const API_BASE = '/api/v1'; // Vite proxy will handle this

export const useApi = () => {
  const { sessionId, region, clearSession } = useSession();

  const apiFetch = useCallback(async (endpoint, options = {}) => {
    const token = localStorage.getItem('aura_token');
    const headers = {
      'Content-Type': 'application/json',
      'X-Session-ID': sessionId || '',
      'X-User-Region': region,
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    };

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      if (response.status === 404) {
        // Session might be expired
        clearSession();
        window.location.href = '/';
        return null;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }, [sessionId, region, clearSession]);

  return useMemo(() => ({ apiFetch }), [apiFetch]);
};
