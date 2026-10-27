import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../services/api';

const Processing = () => {
  const navigate = useNavigate();
  const [statusText, setStatusText] = useState("Analyzing your symptoms...");
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const statusOptions = [
      "Analyzing your symptoms...",
      "Checking safety indicators...",
      "Preparing your assessment..."
    ];
    const statusInterval = setInterval(() => {
      setStatusText(prev => {
        const currentIndex = statusOptions.indexOf(prev);
        return statusOptions[(currentIndex + 1) % statusOptions.length];
      });
    }, 3000);

    return () => clearInterval(statusInterval);
  }, []);

  useEffect(() => {
    const pollResult = async () => {
      try {
        const sessionId = sessionStorage.getItem('aura_session_id');
        if (!sessionId) {
            navigate('/dashboard');
            return;
        }
        
        const data = await api.getResult(sessionId);
        if (data && data.triage_level) {
          // Instead of navigating to just result, store it maybe? We can fetch it in Result.jsx too.
          // In the new layout it's /assessment/result
          navigate('/assessment/result');
        }
      } catch {
        if (retryCount > 15) {
           setStatusText("Taking longer than expected...");
        }
        setRetryCount(prev => prev + 1);
      }
    };

    const interval = setInterval(pollResult, 2000);
    return () => clearInterval(interval);
  }, [navigate, retryCount]);

  const handleCancel = () => {
    sessionStorage.removeItem('aura_session_id');
    navigate('/dashboard');
  };

  return (
    <div className="processing-container" role="status" aria-live="polite">
      <div className="processing-content">
        <div className="pulsing-orb" aria-label="Processing"></div>
        <h2 className="status-text" style={{fontWeight: 700, marginTop: '2rem'}}>{statusText}</h2>
        <p style={{color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto'}}>Our AI is analyzing your responses against medical databases to provide a preliminary assessment.</p>
        <button onClick={handleCancel} className="btn-link" style={{marginTop: '3rem', color: 'var(--accent-purple)', textDecoration: 'none', fontWeight: 600}}>
          Stop analysis and go back
        </button>
      </div>
    </div>
  );
};

export default Processing;
