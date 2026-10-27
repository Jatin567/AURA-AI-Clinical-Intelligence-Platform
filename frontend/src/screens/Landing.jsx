import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../context/SessionContext';
import { useApi } from '../hooks/useApi';
import { Search, ShieldAlert, Sparkles, Activity, Clock } from 'lucide-react';

const Landing = () => {
  const { setSessionId, clearSession } = useSession();
  const { apiFetch } = useApi();
  const navigate = useNavigate();

  useEffect(() => {
    clearSession();
  }, [clearSession]);

  const handleStart = async () => {
    try {
      const data = await apiFetch('/session', { method: 'POST' });
      if (data && data.session_id) {
        setSessionId(data.session_id);
        navigate('/intake');
      }
    } catch (error) {
      console.error('Start error:', error);
      alert('Unable to start session.');
    }
  };

  return (
    <div className="landing-page-container">
      <div className="hero-section">
        <h1 className="hero-title">Dr.Bot</h1>
        <p className="hero-description">
          The chatbot aims to bridge the communication gap in healthcare by offering 24/7 support,
          answering frequently asked questions, guiding patients through pre-appointment preparation,
          and providing general medical advice based on input from licensed professionals.
        </p>

        <div className="search-starter" onClick={handleStart}>
          <Search className="search-icon" size={20} />
          <span className="search-placeholder">How can I help you today?</span>
          <div className="search-enter">Start Assessment</div>
        </div>
      </div>

      <div className="feature-grid">
        <div className="feature-card">
          <div className="card-header">
            <span className="card-number">01</span>
            <Activity size={20} className="card-icon" />
          </div>
          <h3 className="card-title">Triage Engine</h3>
          <p className="card-text">AI-driven assessment to determine clinical urgency and next steps.</p>
        </div>

        <div className="feature-card highlighted">
          <div className="card-header">
            <span className="card-number">02</span>
            <Sparkles size={20} className="card-icon" />
          </div>
          <h3 className="card-title">GenEx Diagnostics</h3>
          <p className="card-text">Detailed analysis of symptoms compared against medical datasets.</p>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-number">03</span>
            <Clock size={20} className="card-icon" />
          </div>
          <h3 className="card-title">24/7 Availability</h3>
          <p className="card-text">Immediate guidance for non-emergency medical inquiries anytime.</p>
        </div>
      </div>

      <div className="safety-footer-notice">
        <ShieldAlert size={18} />
        <p>AURA is an AI assistant, not a doctor. In case of emergency, call local emergency services immediately.</p>
      </div>
    </div>
  );
};

export default Landing;
