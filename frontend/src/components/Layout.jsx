import React, { useState } from 'react';
import { useOutlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { cn } from '../lib/utils';
import { 
  MessageSquarePlus, 
  MessageSquare, 
  ClipboardList, 
  Activity, 
  FileText, 
  LayoutDashboard, 
  Settings, 
  LogOut,
  User,
  PanelLeftClose,
  PanelLeftOpen,
  Search
} from 'lucide-react';

export const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const outlet = useOutlet();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleLogout = async () => {
    await logout();
    navigate('/auth');
  };

  const navItems = [
    { name: 'New Chat', path: '/dashboard', icon: MessageSquarePlus },
    { name: 'Conversations', path: '/history', icon: MessageSquare },
    { name: 'Assessments', path: '/assessments', icon: ClipboardList },
    { name: 'Timeline', path: '/timeline', icon: Activity },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Diagnostics', path: '/diagnostics', icon: Activity },
    { name: 'Workspace', path: `/workspace/${user?.[0]?.patient_id || 'default'}`, icon: LayoutDashboard },
  ];

  return (
    <div className="h-screen w-full flex bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30">
      
      {/* Animated Left Sidebar */}
      <motion.nav 
        initial={false}
        animate={{ width: isSidebarOpen ? 260 : 72 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="h-screen bg-card border-r border-border flex flex-col flex-shrink-0 z-20 relative"
      >
        {/* Toggle Button */}
        <button 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="absolute -right-3.5 top-8 bg-card border border-border rounded-full p-1 text-muted-foreground hover:text-foreground shadow-sm transition-colors z-30 hidden md:block"
        >
          {isSidebarOpen ? <PanelLeftClose size={16} /> : <PanelLeftOpen size={16} />}
        </button>

        {/* Logo Area */}
        <div className={cn("px-4 py-6 flex items-center gap-3", isSidebarOpen ? "mb-4" : "mb-4 justify-center")}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-emerald-400 flex items-center justify-center text-white shadow-lg shadow-blue-900/20 shrink-0">
            <Activity size={20} strokeWidth={2.5} />
          </div>
          <AnimatePresence>
            {isSidebarOpen && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden whitespace-nowrap"
              >
                <h1 className="text-xl font-semibold tracking-tight text-foreground leading-none">AURA</h1>
                <p className="text-[10px] text-muted-foreground font-semibold tracking-widest uppercase mt-1">Health OS</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Search / Global Action (Optional) */}
        {isSidebarOpen && (
          <div className="px-4 mb-6">
            <div className="flex items-center gap-2 px-3 py-2 bg-secondary/50 border border-border/50 rounded-lg text-muted-foreground text-sm cursor-text hover:bg-secondary transition-colors">
              <Search size={16} />
              <span>Search...</span>
              <span className="ml-auto text-[10px] bg-background px-1.5 py-0.5 rounded border border-border">⌘K</span>
            </div>
          </div>
        )}

        <div className="px-4 mb-2">
          {isSidebarOpen && <div className="text-xs font-semibold text-muted-foreground/70 tracking-wider mb-2 uppercase px-2">Menu</div>}
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 custom-scrollbar flex flex-col gap-2 pt-2">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path.split('/')[1] ? `/${item.path.split('/')[1]}` : item.path);
            const Icon = item.icon;
            
            return (
              <Link 
                key={item.name}
                to={item.path} 
                className="relative group outline-none"
              >
                {isActive && (
                  <motion.div
                    layoutId="active-nav"
                    className="absolute inset-0 bg-secondary rounded-xl shadow-sm"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                
                <div className={cn(
                  "relative flex items-center rounded-xl transition-all duration-300 px-3 py-3",
                  !isActive && "hover:bg-secondary/40 text-muted-foreground hover:text-foreground",
                  isActive && "text-foreground",
                  !isSidebarOpen && "justify-center"
                )}>
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: isActive ? 0 : -5 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                  >
                    <Icon size={20} className={cn("shrink-0 transition-colors", isActive && "text-accent")} strokeWidth={isActive ? 2.5 : 2} />
                  </motion.div>
                  
                  <AnimatePresence>
                    {isSidebarOpen && (
                      <motion.span 
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: "auto" }}
                        exit={{ opacity: 0, width: 0 }}
                        className="ml-4 text-[15px] font-medium whitespace-nowrap overflow-hidden"
                      >
                        {item.name}
                      </motion.span>
                    )}
                  </AnimatePresence>

                  {/* Tooltip for collapsed state */}
                  {!isSidebarOpen && (
                    <div className="absolute left-full ml-4 px-2 py-1 bg-popover border border-border text-popover-foreground text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-lg">
                      {item.name}
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
        
        {/* Bottom Profile / Settings */}
        <div className="mt-auto border-t border-border/30 bg-card p-4 flex flex-col gap-2 relative z-30">
          
          <Link to="/profile" className="group relative outline-none">
            <div className={cn("flex items-center rounded-xl px-3 py-3 hover:bg-secondary/40 transition-all duration-300 text-muted-foreground hover:text-foreground", !isSidebarOpen && "justify-center")}>
              <motion.div whileHover={{ scale: 1.1 }} transition={{ type: "spring", stiffness: 400, damping: 10 }}>
                <User size={20} className="shrink-0" />
              </motion.div>
              <AnimatePresence>
                {isSidebarOpen && (
                  <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="ml-4 text-[15px] font-medium whitespace-nowrap overflow-hidden">
                    {user?.[0]?.first_name || 'Profile'}
                  </motion.span>
                )}
              </AnimatePresence>
              {!isSidebarOpen && (
                <div className="absolute left-full ml-4 px-2 py-1 bg-popover border border-border text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-lg text-foreground">
                  Profile
                </div>
              )}
            </div>
          </Link>
          
          <Link to="/settings" className="group relative outline-none">
            <div className={cn("flex items-center rounded-xl px-3 py-3 hover:bg-secondary/40 transition-all duration-300 text-muted-foreground hover:text-foreground", !isSidebarOpen && "justify-center")}>
              <motion.div whileHover={{ scale: 1.1, rotate: 45 }} transition={{ type: "spring", stiffness: 400, damping: 10 }}>
                <Settings size={20} className="shrink-0" />
              </motion.div>
              <AnimatePresence>
                {isSidebarOpen && (
                  <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="ml-4 text-[15px] font-medium whitespace-nowrap overflow-hidden">
                    Settings
                  </motion.span>
                )}
              </AnimatePresence>
              {!isSidebarOpen && (
                <div className="absolute left-full ml-4 px-2 py-1 bg-popover border border-border text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-lg text-foreground">
                  Settings
                </div>
              )}
            </div>
          </Link>
          
          <button onClick={handleLogout} className="group relative outline-none w-full text-left">
            <div className={cn("flex items-center rounded-xl px-3 py-3 hover:bg-destructive/10 transition-all duration-300 text-muted-foreground hover:text-destructive", !isSidebarOpen && "justify-center")}>
              <motion.div whileHover={{ scale: 1.1, x: 2 }} transition={{ type: "spring", stiffness: 400, damping: 10 }}>
                <LogOut size={20} className="shrink-0" />
              </motion.div>
              <AnimatePresence>
                {isSidebarOpen && (
                  <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="ml-4 text-[15px] font-medium whitespace-nowrap overflow-hidden">
                    Log out
                  </motion.span>
                )}
              </AnimatePresence>
              {!isSidebarOpen && (
                <div className="absolute left-full ml-4 px-2 py-1 bg-popover border border-border text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-lg text-foreground">
                  Log out
                </div>
              )}
            </div>
          </button>
          
        </div>
      </motion.nav>

      {/* Main Content Area (Chat Canvas) */}
      <main className="flex-1 h-full relative overflow-hidden bg-background">
        <AnimatePresence mode="wait" initial={false}>
          {outlet && React.cloneElement(outlet, { key: location.pathname, isSidebarOpen })}
        </AnimatePresence>
      </main>

    </div>
  );
};
