import { useState } from 'react';
import { usePatientTimeline } from '../hooks/useAuraData';
import { useAuth } from '../context/AuthContext';
import { PageTransition } from '../components/PageTransition';
import { Search, Filter, Activity, FileText, CheckCircle, AlertTriangle, Info, RefreshCcw } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

export default function Timeline() {
  const [activeFilter, setActiveFilter] = useState('All Activity');
  const { user } = useAuth();
  
  // Use patient_id from auth context or fallback
  const patientId = user?.[0]?.patient_id || 'default_patient';
  
  const { data, isLoading, isError, error } = usePatientTimeline(patientId);

  return (
    <PageTransition>
      <div className="flex h-full w-full bg-background text-foreground">
        {/* Center Content Area */}
        <div className="flex-1 flex flex-col h-full border-r border-border">
          
          {/* Top Header with Filters */}
          <header className="px-8 pt-8 pb-6 border-b border-border shrink-0 bg-background">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-foreground tracking-tight">Patient Timeline</h1>
              
              <div className="flex items-center gap-2">
                <div className="relative w-64 rounded transition-all duration-200">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                  <input className="w-full bg-secondary/50 border border-border rounded-md py-1.5 pl-9 pr-3 text-sm text-foreground focus:outline-none focus:border-primary placeholder:text-muted-foreground h-9" placeholder="Search events..." type="text"/>
                </div>
                <button className="h-9 w-9 rounded-md border border-border bg-secondary/50 flex items-center justify-center text-muted-foreground hover:text-foreground hover:border-border/80 transition-colors">
                  <Filter size={16} />
                </button>
              </div>
            </div>

            {/* Filter Pills */}
            <div className="flex gap-2">
              {['All Activity', 'Conversations', 'Assessments'].map((filter) => (
                <button 
                  key={filter}
                  onClick={() => setActiveFilter(filter)}
                  className={cn(
                    "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors border",
                    activeFilter === filter 
                      ? "bg-primary/10 border-primary text-primary" 
                      : "bg-transparent border-border text-muted-foreground hover:text-foreground"
                  )}
                >
                  {activeFilter === filter && <span className="w-1.5 h-1.5 rounded-full bg-primary" />}
                  {filter}
                </button>
              ))}
            </div>
          </header>

          {/* Timeline Feed */}
          <div className="flex-1 overflow-y-auto p-8 pt-10 relative custom-scrollbar">
            {/* Vertical Line */}
            <div className="absolute left-[47px] top-0 bottom-0 w-px bg-border"></div>
            
            <div className="max-w-[800px] space-y-8 relative z-10">
              
              {isLoading && (
                <div className="space-y-6">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-secondary border border-border shrink-0 mt-1 animate-pulse" />
                      <div className="flex-1 bg-card border border-border rounded-xl p-5 space-y-3 animate-pulse">
                        <div className="h-4 bg-secondary rounded w-1/3"></div>
                        <div className="h-3 bg-secondary rounded w-1/4"></div>
                        <div className="h-16 bg-secondary rounded w-full"></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {isError && (
                <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
                  <div className="bg-destructive/5 border border-destructive/20 rounded-xl p-8 flex flex-col items-center justify-center text-center mt-6">
                    <div className="w-12 h-12 bg-destructive/10 rounded-full flex items-center justify-center mb-4">
                      <AlertTriangle className="text-destructive" size={24} />
                    </div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">Failed to load timeline</h3>
                    <p className="text-sm text-muted-foreground max-w-md mb-6 leading-relaxed">
                      {error?.message || "An unexpected error occurred while fetching your patient timeline."}
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

              {!isLoading && !isError && data && data.overall_summary && !data.overall_summary.startsWith("0 assessments") && (
                <>
                  <TimelineEvent 
                    icon={Activity} 
                    title="Overall Health Summary"
                    color="text-emerald-400"
                    bgColor="bg-emerald-400/10"
                    borderColor="border-emerald-400/20"
                    content={data.overall_summary}
                  />
                  <TimelineEvent 
                    icon={AlertTriangle} 
                    title="Severity Progression"
                    color="text-amber-400"
                    bgColor="bg-amber-400/10"
                    borderColor="border-amber-400/20"
                    content={data.severity_summary}
                  />
                  <TimelineEvent 
                    icon={Info} 
                    title="Symptom Tracking"
                    color="text-blue-400"
                    bgColor="bg-blue-400/10"
                    borderColor="border-blue-400/20"
                    content={data.symptom_summary}
                  />
                  <TimelineEvent 
                    icon={FileText} 
                    title="Diagnostic Conditions"
                    color="text-purple-400"
                    bgColor="bg-purple-400/10"
                    borderColor="border-purple-400/20"
                    content={data.condition_summary}
                  />
                  <TimelineEvent 
                    icon={CheckCircle} 
                    title="Recommendations & Actions"
                    color="text-emerald-400"
                    bgColor="bg-emerald-400/10"
                    borderColor="border-emerald-400/20"
                    content={data.recommendation_summary}
                  />
                </>
              )}

              {!isLoading && !isError && (!data || !data.overall_summary || data.overall_summary.startsWith("0 assessments")) && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8">
                  <div className="bg-card border border-dashed border-border rounded-2xl p-10 flex flex-col items-center justify-center text-center shadow-sm">
                    <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mb-6 border border-border/50">
                      <Activity className="text-muted-foreground" size={28} />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">No Timeline Events Recorded</h3>
                    <p className="text-sm text-muted-foreground max-w-md mb-8 leading-relaxed">
                      The patient timeline tracks significant health events, assessments, and symptom progression. Complete an assessment to start building the timeline.
                    </p>
                  </div>
                </motion.div>
              )}

            </div>
          </div>
        </div>

        {/* Right Context Panel (Static for now, can be updated later) */}
        <aside className="w-[320px] h-full bg-card/50 flex-shrink-0 flex flex-col border-l border-border">
          <div className="p-6">
            <h3 className="text-sm font-semibold text-muted-foreground mb-4">Patient Details</h3>
            <div className="bg-card border border-border rounded-xl p-5 mb-6">
              <p className="text-sm text-foreground">Patient: {patientId}</p>
              <p className="text-xs text-muted-foreground mt-1">Timeline generated dynamically based on active events.</p>
            </div>
          </div>
        </aside>
      </div>
    </PageTransition>
  );
}

function TimelineEvent({ icon: Icon, title, content, color, bgColor, borderColor }) {
  if (!content) return null;
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-4"
    >
      <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 border", bgColor, borderColor)}>
        <Icon className={color} size={16} />
      </div>
      <div className="flex-1 bg-card border border-border rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold tracking-wide text-foreground mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{content}</p>
      </div>
    </motion.div>
  );
}
