/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from 'react';
import * as api from '../services/api';
import { auth, googleProvider, signInWithPopup } from '../lib/firebase';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [firebaseConfigured, setFirebaseConfigured] = useState(true);

  useEffect(() => {
    const checkEnv = () => {
      const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
      const authDomain = import.meta.env.VITE_FIREBASE_AUTH_DOMAIN;
      const projectId = import.meta.env.VITE_FIREBASE_PROJECT_ID;
      if (!apiKey || !authDomain || !projectId) {
        setFirebaseConfigured(false);
      }
    };
    checkEnv();

    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('aura_token');
        if (token) {
          // Use /api/auth/me which returns {user_id, is_active} — always an object,
          // not /api/patients/me which returns [] for users without a PatientProfile.
          const identity = await api.getAuthMe();
          setUser(identity);
        }
      } catch (err) {
        console.error('Auth check failed:', err);
        localStorage.removeItem('aura_token');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!auth) {
        throw new Error("Google authentication is not configured.");
      }

      const result = await signInWithPopup(auth, googleProvider);
      const idToken = await result.user.getIdToken();
      
      const data = await api.loginWithGoogleToken(idToken);
      localStorage.setItem('aura_token', data.session_id);

      const identity = await api.getAuthMe();
      setUser(identity);
      return true;
    } catch (err) {
      console.error(err);
      setError(err.message || 'Google Sign-In failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.login(email, password);
      localStorage.setItem('aura_token', data.session_id);

      const identity = await api.getAuthMe();
      setUser(identity);
      return true;
    } catch (err) {
      setError(err.message || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.register(email, password);
      localStorage.setItem('aura_token', data.session_id);

      const identity = await api.getAuthMe();
      setUser(identity);
      return true;
    } catch (err) {
      setError(err.message || 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.logout();
      // Guard: auth is null when Firebase env vars are not configured.
      if (auth) {
        await auth.signOut();
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('aura_token');
      setUser(null);
    }
  };

  const value = {
    user,
    loading,
    error,
    firebaseConfigured,
    login,
    register,
    loginWithGoogle,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
