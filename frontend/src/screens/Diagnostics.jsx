import { useState, useEffect } from 'react';
import { PageTransition } from '../components/PageTransition';
import { Activity, Database, Zap, Server, Cpu, RefreshCw, CheckCircle, XCircle, AlertCircle, Clock } from 'lucide-react';
import { API_BASE } from '../services/api';

const STATUS_CONFIG = {
  UP:                 { color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20', icon: CheckCircle,   label: 'UP' },
  CONNECTED:          { color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20', icon: CheckCircle,   label: 'CONNECTED' },
  CONFIGURED:         { color: 'text-blue-400',    bg: 'bg-blue-500/10 border-blue-500/20',       icon: CheckCircle,   label: 'CONFIGURED' },
  IN_MEMORY_FALLBACK: { color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/20',     icon: AlertCircle,   label: 'IN-MEMORY' },
  OPTIONAL:           { color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/20',     icon: AlertCircle,   label: 'OPTIONAL' },
  NOT_RUNNING:        { color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/20',     icon: AlertCircle,   label: 'STANDALONE' },
  NOT_CONFIGURED:     { color: 'text-muted-foreground', bg: 'bg-secondary/50 border-border',      icon: AlertCircle,   label: 'NOT CONFIGURED' },
  UNREACHABLE:        { color: 'text-red-400',     bg: 'bg-red-500/10 border-red-500/20',         icon: XCircle,       label: 'UNREACHABLE' },
  KEY_INVALID:        { color: 'text-red-400',     bg: 'bg-red-500/10 border-red-500/20',         icon: XCircle,       label: 'KEY INVALID' },
};

function getStatusConfig(status) {
  if (!status) return STATUS_CONFIG.NOT_CONFIGURED;
  const key = status.toUpperCase();
  if (STATUS_CONFIG[key]) return STATUS_CONFIG[key];
  if (key.startsWith('ERROR_') || key.startsWith('KEY_')) return STATUS_CONFIG.UNREACHABLE;
  if (key.startsWith('PROVIDER_')) return { ...STATUS_CONFIG.CONFIGURED, label: status };
  return STATUS_CONFIG.NOT_CONFIGURED;
}

function StatusBadge({ status }) {
  const cfg = getStatusConfig(status);
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${cfg.bg} ${cfg.color}`}>
      <Icon size={12} />
      {cfg.label}
    </span>
  );
}

function ServiceCard({ icon: Icon, title, status, detail, extra }) {
  const cfg = getStatusConfig(status);
  return (
    <div className={`bg-card border rounded-xl p-5 shadow-sm flex flex-col gap-3 transition-all border-border hover:border-border/80`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl ${cfg.bg}`}>
            <Icon size={18} className={cfg.color} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">{title}</h3>
            {detail && <p className="text-xs text-muted-foreground mt-0.5">{detail}</p>}
          </div>
        </div>
        <StatusBadge status={status} />
      </div>
      {extra && (
        <div className="pt-2 border-t border-border/30 text-xs text-muted-foreground">
          {extra}
        </div>
      )}
    </div>
  );
}

export default function Diagnostics() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastFetched, setLastFetched] = useState(null);

  const fetchHealth = async () => {
    try {
      setError(null);
      const token = localStorage.getItem('aura_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await fetch(`${API_BASE}/diagnostics/health`, { headers });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setHealth(data);
      setLastFetched(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, []);

  return (
    <PageTransition>
      <div className="flex flex-col h-full w-full bg-background text-foreground p-8 overflow-y-auto custom-scrollbar">
        <header className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">System Diagnostics</h1>
            <p className="text-muted-foreground mt-1 text-sm">Real-time system health and service status</p>
          </div>
          <div className="flex items-center gap-3">
            {lastFetched && (
              <span className="text-xs text-muted-foreground flex items-center gap-1.5">
                <Clock size={12} />
                Updated {lastFetched.toLocaleTimeString()}
              </span>
            )}
            <button
              onClick={fetchHealth}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary hover:bg-secondary/80 text-sm font-medium transition-colors"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
        </header>

        {loading && !health && (
          <div className="flex items-center justify-center h-64">
            <div className="flex flex-col items-center gap-3">
              <Activity size={32} className="text-muted-foreground animate-pulse" />
              <p className="text-sm text-muted-foreground">Checking system status...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-destructive/10 text-destructive p-4 rounded-xl border border-destructive/20 mb-8">
            <h3 className="font-semibold text-sm">Failed to load diagnostics</h3>
            <p className="text-xs mt-1 opacity-80">{error}</p>
          </div>
        )}

        {health && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ServiceCard
              icon={Server}
              title="Backend API"
              status={health.backend?.status}
              detail="FastAPI server"
              extra={`Uptime: ${health.backend?.uptime_human || '—'}`}
            />
            <ServiceCard
              icon={Zap}
              title="LLM Service"
              status={(health.llm || health.gemini)?.status}
              detail={`${(health.llm || health.gemini)?.provider || 'LLM'} · ${(health.llm || health.gemini)?.model || '—'}`}
              extra={(health.llm || health.gemini)?.status === 'CONNECTED' ? 'API key verified and reachable' : 'Check LLM_API_KEY in .env'}
            />
            <ServiceCard
              icon={Database}
              title="Database"
              status={health.database?.status}
              detail={health.database?.engine || 'PostgreSQL'}
              extra="Triage sessions and patient data"
            />
            <ServiceCard
              icon={Activity}
              title="Redis / Session Store"
              status={health.redis?.status}
              detail="Session state storage"
              extra={health.redis?.note}
            />
            <ServiceCard
              icon={Cpu}
              title="Clinical Engine"
              status={health.clinical_engine?.status}
              detail="Deterministic safety reasoning"
              extra={health.clinical_engine?.components?.join(' · ')}
            />
          </div>
        )}

        {health && (
          <div className="mt-8 p-5 bg-card border border-border rounded-xl">
            <h2 className="text-sm font-semibold mb-3 text-foreground">Architecture Notes</h2>
            <div className="space-y-1.5 text-xs text-muted-foreground">
              <p>• Clinical decisions (severity, red flags, OTC safety) are <strong className="text-foreground">strictly deterministic</strong> — never LLM-driven</p>
              <p>• LLM (Nemotron / Gemini) is used strictly to <strong className="text-foreground">explain</strong> deterministic results in patient-friendly language</p>
              <p>• Emergency detection always produces an immediate deterministic response — LLM is completely bypassed</p>
              <p>• Conversations and sessions are persistent (<code className="bg-secondary px-1 rounded">app/data/conversations/</code>)</p>
            </div>
          </div>
        )}
      </div>
    </PageTransition>
  );
}
