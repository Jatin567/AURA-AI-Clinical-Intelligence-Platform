import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../services/api';
import { Activity, Sparkles, ShieldAlert, FileText } from 'lucide-react';
import CrisisBanner from '../components/CrisisBanner';
import SeverityBanner from '../components/SeverityBanner';
import OTCCard from '../components/OTCCard';

const Result = () => {
  const navigate = useNavigate();
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [canReset, setCanReset] = useState(true);
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const sessionId = sessionStorage.getItem('aura_session_id');
        if (!sessionId) {
            navigate('/dashboard');
            return;
        }
        
        const data = await api.getResult(sessionId);
        if (data) {
          setResult(data);
          
          // Safety requirement: EMERGENCY/URGENT forced delay
          if (['EMERGENCY', 'URGENT'].includes(data.triage_level)) {
            setCanReset(false);
            setCountdown(5);
            const timer = setInterval(() => {
              setCountdown(prev => {
                if (prev <= 1) {
                  clearInterval(timer);
                  setCanReset(true);
                  return 0;
                }
                return prev - 1;
              });
            }, 1000);
          }
        }
      } catch (error) {
        console.error('Failed to fetch result:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [navigate]);

  const handleNewAssessment = () => {
    sessionStorage.removeItem('aura_session_id');
    navigate('/dashboard');
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) return <div className="processing-container"><p>Finalizing your report...</p></div>;
  if (!result) return <div className="container">Error loading result.</div>;

  const isCrisis = result.crisis_resources && result.crisis_resources.length > 0;

  return (
    <div className="result-page-container" style={{paddingBottom: '4rem'}}>
      {isCrisis && <CrisisBanner resources={result.crisis_resources} />}

      <div className="result-header-panel">
        <SeverityBanner level={result.triage_level} label={result.triage_label} />
        <h1 className="hero-title" style={{fontSize: '2.5rem', marginTop: '1rem'}}>Your AI Health Assessment</h1>
        <p className="hero-description" style={{maxWidth: '600px'}}>{result.explanation}</p>
      </div>

      <div className="feature-grid" style={{maxWidth: '1200px', margin: '0 auto'}}>
        {/* Action Items */}
        <div className="feature-card">
          <div className="card-header">
            <span className="card-number">01</span>
            <Activity size={20} />
          </div>
          <h3 className="card-title">Next Steps</h3>
          <ul className="action-list" style={{listStyle: 'none', padding: 0, margin: 0}}>
            {result.action_items.map((item, idx) => (
              <li key={idx} style={{display: 'flex', gap: '0.75rem', marginBottom: '0.75rem', fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                <div style={{width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--accent-purple)', marginTop: '0.5rem'}}></div>
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Medication */}
        <div className="feature-card highlighted">
          <div className="card-header">
            <span className="card-number">02</span>
            <Sparkles size={20} />
          </div>
          <h3 className="card-title">Recommendations</h3>
          <div className="otc-list">
            {result.approved_otc_suggestions.length > 0 ? (
              result.approved_otc_suggestions.map((sugg, idx) => (
                <div key={idx} style={{marginBottom: '1rem', padding: '1rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)'}}>
                  <div style={{fontWeight: 700, fontSize: '0.9375rem'}}>{sugg.name}</div>
                  <div style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>{sugg.reason}</div>
                </div>
              ))
            ) : (
              <p className="card-text italic">No specific medications suggested.</p>
            )}
          </div>
        </div>

        {/* Safety */}
        <div className="feature-card">
          <div className="card-header">
            <span className="card-number">03</span>
            <ShieldAlert size={20} />
          </div>
          <h3 className="card-title">Safety Notice</h3>
          <p className="card-text">{result.medical_disclaimer}</p>
        </div>
      </div>

      {/* Clinical Reasoning Intelligence Breakdown (Internal Demo Feature) */}
      {result.clinical_reasoning && (
        <div style={{maxWidth: '1200px', margin: '3rem auto 0 auto', padding: '1.5rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)'}}>
          <h3 style={{fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--accent-purple)', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Sparkles size={18} /> Deterministic Clinical Reasoning Core (V2 Demo)
          </h3>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem'}}>
            
            {/* Differentials */}
            <div>
              <h4 style={{fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--text-primary)'}}>Differential Candidates</h4>
              {result.clinical_reasoning.possible_conditions?.slice(0, 3).map((cond, idx) => (
                <div key={idx} style={{marginBottom: '0.75rem', padding: '0.75rem', backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: '4px'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', fontWeight: 600, fontSize: '0.875rem'}}>
                    <span>{cond.name} <span style={{fontSize: '0.75rem', opacity: 0.7}}>({cond.icd10_code})</span></span>
                    <span style={{color: 'var(--accent-purple)'}}>{(cond.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem'}}>
                    Supporting: {cond.supporting_symptoms.join(', ') || 'None'}
                  </div>
                </div>
              ))}
            </div>

            {/* Risk Factors */}
            <div>
              <h4 style={{fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--text-primary)'}}>Risk Factors Evaluated</h4>
              {result.clinical_reasoning.risk_factors?.length > 0 ? (
                result.clinical_reasoning.risk_factors.map((rf, idx) => (
                  <div key={idx} style={{marginBottom: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-secondary)'}}>
                    <strong style={{color: 'var(--text-primary)'}}>• {rf.factor_name}</strong> (+{rf.risk_weight})
                  </div>
                ))
              ) : (
                <p style={{fontSize: '0.8125rem', color: 'var(--text-muted)'}}>No elevated risk factors detected.</p>
              )}
            </div>

          </div>
        </div>
      )}

      <div className="footer-actions" style={{marginTop: '4rem', display: 'flex', justifyContent: 'center', gap: '1.5rem'}}>
          <button 
            onClick={handleNewAssessment} 
            disabled={!canReset}
            className="chat-send-btn"
            style={{padding: '1rem 2rem', borderRadius: 'var(--radius-md)', fontWeight: 700, opacity: !canReset ? 0.5 : 1}}
          >
            {canReset ? 'Start New Checkup' : `Reviewing... (${countdown}s)`}
          </button>
          
          <button onClick={handlePrint} className="action-btn" style={{padding: '1rem 2rem', borderRadius: 'var(--radius-md)'}}>
            Download Report
          </button>
      </div>
    </div>
  );
};

export default Result;
