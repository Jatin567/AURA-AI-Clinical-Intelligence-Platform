import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useWorkspaceData } from '../hooks/useAuraData';
import { PageTransition } from '../components/PageTransition';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';
import { 
  Search, Bell, HelpCircle, Activity, 
  MessageSquare, BrainCircuit, ClipboardCheck, 
  AlertTriangle, RefreshCcw, Plus
} from 'lucide-react';

export default function Workspace() {
  const { patientId = 'default_patient' } = useParams();
  const navigate = useNavigate();
  
  // In a real flow, we'd retrieve this from context or another API.
  // We leave these null to demonstrate the onboarding/empty state.
  const [reportData] = useState(null);
  const [explanationData] = useState(null);

  const { data, isLoading, isError, error } = useWorkspaceData(patientId, reportData, explanationData);

  const hasRequiredData = Boolean(
    reportData && Object.keys(reportData).length > 0 && 
    explanationData && Object.keys(explanationData).length > 0
  );

  return (
    <PageTransition>
      <div className="flex h-full w-full bg-background text-foreground">
        {/* Center Content Area */}
        <div className="flex-1 flex flex-col h-full border-r border-border">
          
          {/* Top Header */}
          <header className="h-[60px] flex items-center justify-between px-6 border-b border-border shrink-0 bg-background">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Patients</span>
              <span className="text-lg leading-none">›</span>
              <span className="text-foreground">Workspace Overview</span>
            </div>
            <div className="flex items-center gap-4 text-muted-foreground">
              <div className="hidden md:flex relative w-64 rounded transition-all duration-200">
                <Search className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                <input className="w-full bg-transparent border-b border-border py-1.5 pl-8 pr-3 text-sm text-foreground focus:outline-none focus:border-primary placeholder:text-muted-foreground h-8" placeholder="Search insights..." type="text"/>
              </div>
              <button className="hover:text-primary transition-colors"><Bell size={18} /></button>
              <button className="hover:text-primary transition-colors"><HelpCircle size={18} /></button>
              <div className="w-7 h-7 rounded-full bg-secondary border border-border flex items-center justify-center overflow-hidden">
                <img src="https://i.pravatar.cc/150?img=11" alt="User" className="w-full h-full object-cover" />
              </div>
            </div>
          </header>

          {/* Workspace Content */}
          <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
            <div className="max-w-[850px] mx-auto flex flex-col gap-6">
              
              {/* Header Title */}
              <div>
                <div className="flex items-center gap-4 mb-2">
                  <h1 className="text-3xl font-bold text-foreground">Workspace Overview</h1>
                  {hasRequiredData && (
                    <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-card border border-border">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                      <span className="font-mono text-xs text-muted-foreground">Live Sync</span>
                    </div>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  Comprehensive AI-assisted synthesis of current health status, recent assessments, and actionable recommendations.
                </p>
              </div>

              {/* Onboarding / Empty State */}
              {!hasRequiredData && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8">
                  <div className="bg-card border border-dashed border-border rounded-2xl p-10 flex flex-col items-center justify-center text-center shadow-sm">
                    <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mb-6 border border-border/50">
                      <Activity className="text-muted-foreground" size={28} />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">No Active Clinical Report</h3>
                    <p className="text-sm text-muted-foreground max-w-md mb-8 leading-relaxed">
                      This workspace synthesizes patient clinical reports and LLM explanations. To view the workspace, you must first complete a clinical intake assessment.
                    </p>
                    <button 
                      onClick={() => navigate('/dashboard')}
                      className="px-6 py-2.5 bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg font-medium transition-colors flex items-center gap-2 shadow-sm"
                    >
                      <Plus size={18} />
                      Start Assessment
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Loading State */}
              {hasRequiredData && isLoading && (
                <div className="space-y-6">
                  {/* Synthesis Skeleton */}
                  <div className="bg-card border border-border rounded-xl p-6 h-40 animate-pulse flex flex-col gap-3">
                    <div className="w-1/4 h-5 bg-secondary rounded"></div>
                    <div className="w-full h-4 bg-secondary rounded mt-2"></div>
                    <div className="w-5/6 h-4 bg-secondary rounded"></div>
                    <div className="w-3/4 h-4 bg-secondary rounded"></div>
                  </div>
                  {/* Grid Skeletons */}
                  <div className="grid grid-cols-2 gap-6">
                    <div className="bg-card border border-border rounded-xl p-6 h-64 animate-pulse flex flex-col gap-3">
                      <div className="w-1/3 h-5 bg-secondary rounded"></div>
                      <div className="w-1/2 h-6 bg-secondary rounded mt-2"></div>
                      <div className="w-full h-24 bg-secondary rounded mt-auto"></div>
                    </div>
                    <div className="bg-card border border-border rounded-xl p-6 h-64 animate-pulse flex flex-col gap-3">
                      <div className="w-1/3 h-5 bg-secondary rounded"></div>
                      <div className="flex-1 space-y-4 mt-4">
                        <div className="w-full h-4 bg-secondary rounded"></div>
                        <div className="w-full h-4 bg-secondary rounded"></div>
                        <div className="w-full h-4 bg-secondary rounded"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Error State */}
              {hasRequiredData && isError && (
                <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
                  <div className="bg-destructive/5 border border-destructive/20 rounded-xl p-8 flex flex-col items-center justify-center text-center mt-6">
                    <div className="w-12 h-12 bg-destructive/10 rounded-full flex items-center justify-center mb-4">
                      <AlertTriangle className="text-destructive" size={24} />
                    </div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">Workspace Generation Failed</h3>
                    <p className="text-sm text-muted-foreground max-w-md mb-6 leading-relaxed">
                      {error?.message || "An unexpected error occurred while parsing the clinical report."}
                    </p>
                    <button 
                      onClick={() => window.location.reload()}
                      className="px-5 py-2 bg-secondary text-foreground hover:bg-secondary/80 border border-border rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                    >
                      <RefreshCcw size={16} />
                      Retry Generation
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Success State */}
              {hasRequiredData && !isLoading && !isError && data && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                  {/* Conversation Synthesis */}
                  <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                    <div className="flex justify-between items-center mb-4">
                      <div className="flex items-center gap-2 text-foreground text-xs font-mono uppercase tracking-wide">
                        <MessageSquare size={16} />
                        Conversation Synthesis
                      </div>
                    </div>
                    <p className="text-sm leading-relaxed mb-6 text-muted-foreground">
                      {data.patient_summary || "No summary available."}
                    </p>
                    <div className="flex gap-2">
                      <span className="px-3 py-1 bg-secondary/50 border border-border rounded text-xs text-muted-foreground font-mono"># Active Patient</span>
                    </div>
                  </div>

                  {/* Two Column Grid */}
                  <div className="grid grid-cols-2 gap-6">
                    {/* Clinical Explanation */}
                    <div className="bg-card border border-border rounded-xl p-6 flex flex-col h-full shadow-sm">
                      <div className="flex items-center gap-2 text-foreground text-xs font-mono uppercase tracking-wide mb-5">
                        <BrainCircuit size={16} />
                        Primary Condition
                      </div>
                      
                      <div className="mb-4">
                        <h3 className="text-lg font-medium leading-tight">
                          {data.current_assessment?.top_condition?.condition_name || "N/A"}
                        </h3>
                        <div className="text-primary text-xs font-mono mt-1">
                          Confidence: {data.current_assessment?.top_condition?.confidence_score || 0}%
                        </div>
                      </div>
                      
                      <p className="text-sm text-muted-foreground leading-relaxed mb-6 flex-1">
                        {data.current_assessment?.top_condition?.justification || "No justification provided."}
                      </p>
                    </div>

                    {/* Assessment Report */}
                    <div className="bg-card border border-border rounded-xl p-6 flex flex-col h-full shadow-sm">
                      <div className="flex justify-between items-start mb-6">
                        <div className="flex items-center gap-2 text-foreground text-xs font-mono uppercase tracking-wide">
                          <ClipboardCheck size={16} />
                          Risk Factors
                        </div>
                      </div>

                      <div className="space-y-4 flex-1">
                        {data.risk_factors && data.risk_factors.length > 0 ? (
                          data.risk_factors.map((risk, i) => (
                            <div key={i} className="flex justify-between items-center text-sm">
                              <span className="text-muted-foreground">{risk.category}</span>
                              <span className="text-foreground flex items-center gap-2">
                                {risk.level} <span className={cn("w-1.5 h-1.5 rounded-full", risk.level === 'HIGH' ? 'bg-destructive' : 'bg-amber-400')}></span>
                              </span>
                            </div>
                          ))
                        ) : (
                          <div className="text-sm text-muted-foreground">No risk factors identified.</div>
                        )}
                      </div>

                      <button className="w-full py-2.5 bg-secondary hover:bg-secondary/80 border border-border text-foreground text-sm rounded-lg transition-colors mt-6">
                        View Full Details
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>

        {/* Right Context Panel (Static for Now) */}
        <aside className="w-[320px] h-full bg-card/50 flex-shrink-0 flex flex-col overflow-y-auto border-l border-border">
          <div className="p-6">
            {/* Patient Profile Card */}
            <div className="bg-card border border-border rounded-xl p-5 mb-6 shadow-sm">
              <div className="flex items-center gap-4 border-b border-border pb-4 mb-4">
                <div className="w-12 h-12 rounded bg-secondary flex items-center justify-center text-lg font-medium text-foreground">
                  {patientId.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-base font-semibold text-foreground leading-tight mb-1">{patientId}</h2>
                  <p className="text-xs font-mono text-muted-foreground">Active Case</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground text-sm">Status</span>
                  <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-mono text-emerald-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    Active
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </PageTransition>
  );
}
