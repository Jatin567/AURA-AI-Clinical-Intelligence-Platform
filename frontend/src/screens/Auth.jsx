import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, AlertTriangle, ArrowRight, Activity, ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { PageTransition } from '../components/PageTransition';
import { LoadingScreen } from '../components/LoadingScreen';

export default function Auth() {
  const { login, register, loginWithGoogle, error, loading, firebaseConfigured } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  // Map generic errors to specific messages without duplicating derived state.
  const displayError = (() => {
    if (!error) return '';
    const errLower = error.toLowerCase();
    if (errLower.includes('wrong password') || errLower.includes('invalid credentials')) {
      return 'Wrong password or email.';
    } else if (errLower.includes('already registered')) {
      return 'Email already registered.';
    } else if (errLower.includes('not found') || errLower.includes('missing')) {
      return 'User not found.';
    } else if (errLower.includes('expired')) {
      return 'Session expired. Please log in again.';
    } else if (errLower.includes('network') || errLower.includes('fetch')) {
      return 'Network offline. Check your connection.';
    } else if (errLower.includes('firebase')) {
      return 'Firebase authentication unavailable.';
    }
    return 'Backend unavailable or unknown error.';
  })();

  const handleSubmit = async (e) => {
    e.preventDefault();
    let success = false;
    if (isLogin) {
      success = await login(email, password);
    } else {
      success = await register(email, password);
    }
    if (success) {
      navigate('/');
    }
  };

  const handleGoogleLogin = async () => {
    if (!firebaseConfigured) return;
    const success = await loginWithGoogle();
    if (success) {
      navigate('/');
    }
  };

  return (
    <PageTransition>
      {loading && <LoadingScreen message="Authenticating..." />}
      <div className="min-h-screen w-full flex items-center justify-center bg-background text-foreground relative overflow-hidden">
        
        {/* Animated Background Elements */}
        <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
          <motion.div 
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
              rotate: [0, 90, 0]
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute -top-[20%] -left-[10%] w-[50vw] h-[50vw] rounded-full bg-primary/5 blur-[120px]"
          />
          <motion.div 
            animate={{ 
              scale: [1, 1.5, 1],
              opacity: [0.2, 0.4, 0.2],
              x: [0, 100, 0]
            }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute top-[40%] -right-[10%] w-[40vw] h-[40vw] rounded-full bg-blue-500/5 blur-[100px]"
          />
        </div>

        <div className="w-full max-w-[1000px] grid grid-cols-1 md:grid-cols-2 gap-8 p-6 z-10">
          
          {/* Left Branding Panel */}
          <div className="hidden md:flex flex-col justify-center px-12">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
                  <Activity className="text-primary" size={24} />
                </div>
                <span className="text-3xl font-bold tracking-tight">AURA</span>
              </div>
              <h1 className="text-4xl font-bold leading-tight mb-6">
                Clinical Decision <br/> Support System
              </h1>
              <p className="text-lg text-muted-foreground mb-8 max-w-md leading-relaxed">
                AURA combines deterministic clinical reasoning with advanced language models to provide safe, actionable patient insights.
              </p>
              <div className="space-y-4">
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <ShieldCheck className="text-emerald-500" size={20} />
                  Strict deterministic safety boundaries
                </div>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <Activity className="text-blue-500" size={20} />
                  Adaptive clinical interviewing
                </div>
              </div>
            </motion.div>
          </div>

          {/* Right Auth Panel */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="w-full max-w-[420px] mx-auto"
          >
            <div className="bg-card/60 backdrop-blur-xl border border-border/50 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
              {/* Glass reflection */}
              <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent pointer-events-none" />
              
              <div className="relative z-10">
                <h2 className="text-2xl font-semibold mb-2">
                  {isLogin ? 'Welcome back' : 'Create an account'}
                </h2>
                <p className="text-sm text-muted-foreground mb-8">
                  {isLogin ? 'Enter your credentials to access your workspace.' : 'Register to start managing patients.'}
                </p>

                <AnimatePresence>
                  {displayError && (
                    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mb-6">
                      <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 flex items-start gap-3">
                        <AlertTriangle className="text-destructive shrink-0 mt-0.5" size={16} />
                        <span className="text-sm text-destructive font-medium leading-tight">{displayError}</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <button 
                  type="button"
                  onClick={handleGoogleLogin}
                  disabled={loading || !firebaseConfigured}
                  className="w-full flex items-center justify-center gap-3 py-2.5 px-4 bg-secondary hover:bg-secondary/80 border border-border rounded-xl text-sm font-medium transition-all duration-200 mb-6 disabled:opacity-70"
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  {firebaseConfigured ? 'Continue with Google' : 'Google Authentication Not Configured'}
                </button>

                <div className="flex items-center gap-4 mb-6">
                  <div className="flex-1 h-px bg-border/50"></div>
                  <span className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Or email</span>
                  <div className="flex-1 h-px bg-border/50"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Email Address</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                      <input 
                        type="email" 
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        disabled={loading}
                        className="w-full bg-secondary/30 border border-border rounded-xl py-2.5 pl-10 pr-4 text-sm text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all disabled:opacity-50"
                        placeholder="doctor@clinic.com"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Password</label>
                      {isLogin && <a href="#" className="text-xs text-primary hover:underline">Forgot password?</a>}
                    </div>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                      <input 
                        type={showPassword ? "text" : "password"} 
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        disabled={loading}
                        className="w-full bg-secondary/30 border border-border rounded-xl py-2.5 pl-10 pr-10 text-sm text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all disabled:opacity-50"
                        placeholder="••••••••"
                        required
                      />
                      <button 
                        type="button" 
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full py-3 bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl font-medium shadow-lg shadow-primary/20 transition-all duration-200 flex items-center justify-center gap-2 mt-6 disabled:opacity-70"
                  >
                    {loading ? (
                      <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                    ) : (
                      <>
                        {isLogin ? 'Sign In' : 'Create Account'}
                        <ArrowRight size={18} />
                      </>
                    )}
                  </button>
                </form>

                <p className="text-center text-sm text-muted-foreground mt-8">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button 
                    type="button"
                    onClick={() => setIsLogin(!isLogin)} 
                    disabled={loading}
                    className="text-primary font-medium hover:underline disabled:opacity-50"
                  >
                    {isLogin ? 'Sign up' : 'Sign in'}
                  </button>
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
}
