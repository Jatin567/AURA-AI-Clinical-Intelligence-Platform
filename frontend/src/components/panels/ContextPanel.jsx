import React from 'react';
import { useSessionEngine } from '../../engine/SessionEngine';
import { motion, AnimatePresence } from 'framer-motion';
import { X, User, Activity, FileText } from 'lucide-react';

export const ContextPanel = () => {
  const { panelState, closePanel, patientContext } = useSessionEngine();
  const userName = patientContext?.full_name || "Patient";
  
  return (
    <AnimatePresence>
      {panelState.isOpen && (
        <motion.aside 
          className="w-[380px] h-full bg-secondary/95 backdrop-blur-3xl border-l border-border/40 shrink-0 flex flex-col z-50 absolute right-0 top-0 shadow-2xl"
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          role="complementary"
          aria-label="Contextual panel"
        >
          <div className="h-[60px] flex items-center justify-between px-6 border-b border-border/40 shrink-0">
            <h3 className="text-[13px] font-mono text-muted-foreground uppercase tracking-wider font-semibold">
              {panelState.view || 'Patient Context'}
            </h3>
            <button 
              onClick={closePanel} 
              aria-label="Close panel"
              className="p-1.5 rounded-md hover:bg-white/10 text-muted-foreground hover:text-foreground transition-colors"
            >
              <X size={18} />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-8 custom-scrollbar">
            {/* Patient Header */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary/10 border border-border/50 flex items-center justify-center relative overflow-hidden shrink-0">
                 <User size={32} className="text-primary/70" />
              </div>
              <div className="flex flex-col gap-1">
                <h2 className="text-xl font-semibold text-foreground tracking-tight">{userName}</h2>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>ID: {patientContext?.patient_id || '---'}</span>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div className="glass-panel p-4 rounded-xl flex flex-col gap-2 border border-border/30">
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <Activity size={16} className="text-emerald-400" />
                  Health Score
                </div>
                <span className="text-2xl font-semibold text-foreground tracking-tight">85/100</span>
              </div>
              <div className="glass-panel p-4 rounded-xl flex flex-col gap-2 border border-border/30">
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <FileText size={16} className="text-blue-400" />
                  Active Reports
                </div>
                <span className="text-2xl font-semibold text-foreground tracking-tight">2</span>
              </div>
            </div>

            <div className="flex flex-col gap-4">
               <h4 className="text-sm font-semibold text-foreground border-b border-border/40 pb-2">Active Conditions</h4>
               <p className="text-sm text-muted-foreground leading-relaxed">
                 No active critical conditions recorded.
               </p>
            </div>
            
            <div className="flex flex-col gap-4">
               <h4 className="text-sm font-semibold text-foreground border-b border-border/40 pb-2">Current Medications</h4>
               <p className="text-sm text-muted-foreground leading-relaxed">
                 No active medications found in context.
               </p>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};
