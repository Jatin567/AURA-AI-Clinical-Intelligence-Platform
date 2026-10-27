import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCcw, Home } from 'lucide-react';
import { PageTransition } from './PageTransition';

export class GlobalErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // We could log this to Sentry or a backend telemetry service here
    console.error("Global Error Boundary caught:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <PageTransition>
          <div className="flex h-screen w-screen items-center justify-center bg-background p-6">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }} 
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-md w-full bg-card border border-destructive/20 rounded-2xl p-8 shadow-xl text-center flex flex-col items-center"
            >
              <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-6">
                <AlertTriangle className="text-destructive" size={32} />
              </div>
              
              <h1 className="text-2xl font-bold text-foreground mb-3">Something went wrong</h1>
              <p className="text-sm text-muted-foreground mb-8 leading-relaxed">
                AURA encountered an unexpected error while processing your request. Our clinical safety protocols have halted the current operation.
              </p>

              {/* We purposely do NOT show the raw stack trace or Pydantic validation errors to the user */}

              <div className="flex flex-col w-full gap-3">
                <button 
                  onClick={this.handleReset}
                  className="w-full flex items-center justify-center gap-2 py-3 bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl font-medium transition-colors"
                >
                  <Home size={18} />
                  Return to Dashboard
                </button>
                <button 
                  onClick={() => window.location.reload()}
                  className="w-full flex items-center justify-center gap-2 py-3 bg-secondary text-foreground hover:bg-secondary/80 border border-border rounded-xl font-medium transition-colors"
                >
                  <RefreshCcw size={18} />
                  Reload Page
                </button>
              </div>
            </motion.div>
          </div>
        </PageTransition>
      );
    }

    return this.props.children;
  }
}
