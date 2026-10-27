import React, { useState, useEffect, useRef } from 'react';
import { ChatComposer } from '../components/chat/ChatComposer';
import { ChatStream } from '../components/chat/ChatStream';
import { ConversationSidebar } from '../components/chat/ConversationSidebar';
import { ContextPanel } from '../components/panels/ContextPanel';
import { SessionEngineProvider, useSessionEngine } from '../engine/SessionEngine';
import { InteractionEngineProvider } from '../engine/InteractionEngine';
import { ThemeEngineProvider } from '../engine/ThemeEngine';
import { motion } from 'framer-motion';
import { Activity, ShieldAlert, FileText, Pill, Clock, Wifi, Lock } from 'lucide-react';
import { createConversation, getConversationMessages } from '../services/api';

const DashboardContent = () => {
  const { conversationState, updateConversationStatus } = useSessionEngine();
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [triggerStream, setTriggerStream] = useState(null);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const activeConversationIdRef = useRef(null);

  useEffect(() => {
    activeConversationIdRef.current = activeConversationId;
  }, [activeConversationId]);

  
  const suggestedPrompts = [
    { title: "Analyze Symptoms", icon: Activity },
    { title: "Upload Lab Report", icon: FileText },
    { title: "Medication Review", icon: Pill },
    { title: "Health Timeline", icon: Clock },
    { title: "Risk Assessment", icon: ShieldAlert }
  ];

  const currentDate = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  const isDev = import.meta.env.DEV;

  useEffect(() => {
    if (activeConversationId) {
      loadMessages(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  const loadMessages = async (id) => {
    setIsLoadingMessages(true);
    try {
      const data = await getConversationMessages(id);
      setMessages(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const ensureConversation = async (seedText = '') => {
    if (activeConversationIdRef.current) {
      return activeConversationIdRef.current;
    }
    const trimmed = seedText.trim();
    const title = trimmed
      ? (trimmed.length > 48 ? `${trimmed.slice(0, 45)}...` : trimmed)
      : 'New Conversation';
    const conv = await createConversation(title);
    activeConversationIdRef.current = conv.conversation_id;
    setActiveConversationId(conv.conversation_id);
    return conv.conversation_id;
  };

  const handleSendMessage = async (msg) => {
    const text = (msg || '').trim();
    if (!text) return;
    try {
      await ensureConversation(text);
      setTriggerStream(text);
      updateConversationStatus('generating');
    } catch (err) {
      console.error(err);
      updateConversationStatus('idle');
      alert(err.message || 'Unable to start the conversation.');
    }
  };

  const handleStreamEnd = () => {
    setTriggerStream(null);
    updateConversationStatus('idle');
    if (activeConversationId) {
      loadMessages(activeConversationId); // Refresh to get final assistant message from DB
    }
  };

  const isChatActive = messages.length > 0 || conversationState.status === 'generating';

  return (
    <div className="flex h-full w-full bg-background text-foreground overflow-hidden">
      
      {/* Sidebar Area */}
      <ConversationSidebar 
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewConversation={setActiveConversationId}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative border-r border-border/40 transition-all duration-300 min-w-0">
        <header className="h-[60px] flex items-center px-6 border-b border-border/40 shrink-0 bg-background/80 backdrop-blur-md z-10 justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm font-medium tracking-wide">
              <span className="text-foreground">AURA</span>
              <span className="text-muted-foreground">/</span>
              <span className="text-muted-foreground truncate">{activeConversationId ? 'Conversation' : 'New Conversation'}</span>
            </div>
            
            {isDev && (
              <div className="hidden md:flex items-center gap-3 ml-4 pl-4 border-l border-border/40 text-[11px] font-mono text-muted-foreground/70 uppercase tracking-widest">
                <span className="flex items-center gap-1.5"><Lock size={12} className="text-medical-green" /> Secure</span>
                <span className="flex items-center gap-1.5"><Wifi size={12} className="text-accent" /> Connected</span>
                <span>Gemini 3.1 Pro</span>
              </div>
            )}
          </div>
          <div className="text-[11px] font-mono text-muted-foreground/50 uppercase tracking-widest">
            {currentDate}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto w-full flex flex-col items-center custom-scrollbar relative">
          
          {isLoadingMessages ? (
            <div className="flex items-center justify-center h-full">
              <Activity className="animate-spin text-muted-foreground" />
            </div>
          ) : !isChatActive ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto text-center px-4 w-full"
            >
              <div className="relative mb-8 group">
                <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full opacity-50 group-hover:opacity-70 transition-opacity duration-1000"></div>
                <div className="w-20 h-20 rounded-3xl bg-card border border-border/50 flex items-center justify-center relative z-10 shadow-2xl">
                  <Activity size={32} className="text-foreground drop-shadow-md" strokeWidth={2} />
                </div>
              </div>
              
              <h1 className="text-4xl font-medium text-foreground mb-3 tracking-tight glow-text">
                Hello, I'm AURA.
              </h1>
              <p className="text-lg text-muted-foreground mb-12 font-medium">Medical AI Operating System</p>
              
              {/* Only show suggested prompts if no conversation is active */}
              {!activeConversationId && (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 w-full max-w-3xl">
                  {suggestedPrompts.map((prompt, i) => {
                    const Icon = prompt.icon;
                    return (
                      <motion.button
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 + (i * 0.1), type: "spring", stiffness: 300, damping: 25 }}
                        key={i}
                        onClick={() => handleSendMessage(prompt.title)}
                        className="p-5 rounded-2xl border border-border/40 bg-card/50 hover:bg-secondary/50 text-left transition-all duration-300 hover:border-border/80 group hover:-translate-y-1 shadow-sm hover:shadow-md backdrop-blur-sm"
                      >
                        <div className="flex flex-col gap-3">
                          <Icon size={20} className="text-muted-foreground group-hover:text-accent transition-colors" />
                          <p className="text-sm text-muted-foreground font-medium group-hover:text-foreground transition-colors">{prompt.title}</p>
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              )}
            </motion.div>
          ) : (
            <div className="w-full flex-1">
              <ChatStream 
                conversationId={activeConversationId}
                triggerStream={triggerStream} 
                userMessages={messages} 
                onStreamEnd={handleStreamEnd}
              />
            </div>
          )}
        </div>

        {/* Composer Area */}
        <div className="w-full bg-gradient-to-t from-background via-background to-transparent pt-10 pb-6 shrink-0 relative z-20">
          <div className="max-w-3xl mx-auto w-full px-4">
            <ChatComposer 
              activeConversationId={activeConversationId}
              onEnsureConversation={ensureConversation}
              onSendMessage={handleSendMessage} 
              onStopGeneration={() => {
                if (window.abortCurrentStream) {
                  window.abortCurrentStream();
                }
              }}
            />
          </div>
        </div>
      </div>

      <ContextPanel />
    </div>
  );
};

export default function Dashboard() {
  return (
    <SessionEngineProvider>
      <InteractionEngineProvider>
        <ThemeEngineProvider>
          <DashboardContent />
        </ThemeEngineProvider>
      </InteractionEngineProvider>
    </SessionEngineProvider>
  );
}
