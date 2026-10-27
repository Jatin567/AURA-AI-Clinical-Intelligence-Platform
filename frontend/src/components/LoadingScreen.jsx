import React from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';

export const LoadingScreen = ({ message = "Authenticating..." }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="flex flex-col items-center gap-6 p-8 rounded-3xl bg-card border border-border shadow-2xl"
      >
        <div className="relative">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute -inset-4 border-2 border-primary/20 border-t-primary rounded-full"
          />
          <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30">
            <Activity className="text-primary w-8 h-8" />
          </div>
        </div>
        
        <div className="text-center space-y-2">
          <h3 className="text-xl font-semibold tracking-tight">{message}</h3>
          <p className="text-sm text-muted-foreground">Please wait while we secure your connection.</p>
        </div>
      </motion.div>
    </div>
  );
};
