import React, { useState, useEffect } from 'react';
import { Plus, MessageSquare, MoreHorizontal, Trash2, Edit2, Search, PanelLeftClose, PanelLeft, Settings2, Clock } from 'lucide-react';
import { getConversations, createConversation, deleteConversation, renameConversation } from '../../services/api';
import { motion, AnimatePresence } from 'framer-motion';

const formatTimeAgo = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  return date.toLocaleDateString();
};

export const ConversationSidebar = ({ 
  activeConversationId, 
  onSelectConversation, 
  onNewConversation 
}) => {
  const [conversations, setConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (!activeConversationId) return;
    if (conversations.some((c) => c.conversation_id === activeConversationId)) return;
    fetchConversations();
  }, [activeConversationId, conversations]);

  const fetchConversations = async () => {
    try {
      setIsLoading(true);
      const data = await getConversations();
      // Sort by updated_at descending
      setConversations(data.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at)));
    } catch (err) {
      console.error('Failed to load conversations', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const conv = await createConversation("New Conversation");
      setConversations(prev => [conv, ...prev]);
      onNewConversation(conv.conversation_id);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(c => c.conversation_id !== id));
      if (activeConversationId === id) {
        onNewConversation(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const startRename = (id, currentTitle, e) => {
    e.stopPropagation();
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  const submitRename = async (id) => {
    try {
      await renameConversation(id, editTitle);
      setConversations(prev => prev.map(c => c.conversation_id === id ? { ...c, title: editTitle } : c));
      setEditingId(null);
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = conversations.filter(c => c.title.toLowerCase().includes(search.toLowerCase()));

  if (isCollapsed) {
    return (
      <div className="w-[72px] h-full flex flex-col items-center py-6 border-r border-border/40 bg-card z-30 transition-all">
        <button onClick={() => setIsCollapsed(false)} className="p-2.5 hover:bg-secondary rounded-xl mb-4 text-muted-foreground transition-colors">
          <PanelLeft size={20} />
        </button>
        <button onClick={handleCreate} className="p-2.5 bg-accent hover:bg-accent/90 text-accent-foreground rounded-xl shadow-sm transition-colors">
          <Plus size={20} />
        </button>
      </div>
    );
  }

  return (
    <div className="w-[320px] h-full flex flex-col border-r border-border/40 bg-card z-30 transition-all shrink-0">
      <div className="p-4 flex items-center justify-between border-b border-border/20">
        <div className="flex items-center gap-2 text-foreground font-medium text-sm">
          <MessageSquare size={16} className="text-muted-foreground" />
          Conversations
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => setIsCollapsed(true)} className="p-2 hover:bg-secondary rounded-lg text-muted-foreground transition-colors">
            <PanelLeftClose size={16} />
          </button>
          <button onClick={handleCreate} className="p-2 hover:bg-secondary rounded-lg text-muted-foreground hover:text-accent transition-colors">
            <Plus size={16} />
          </button>
        </div>
      </div>
      
      <div className="px-4 py-3">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-2.5 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search chats..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-background border border-border text-sm rounded-xl pl-9 pr-3 py-2 focus:outline-none focus:ring-1 focus:ring-ring transition-shadow"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 custom-scrollbar">
        {isLoading ? (
          <div className="flex flex-col gap-2 mt-2">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-[72px] bg-secondary/30 rounded-xl animate-pulse"></div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center text-sm text-muted-foreground mt-10">
            {search ? 'No results found' : 'No conversations yet.'}
          </div>
        ) : (
          <div className="flex flex-col gap-2 mt-1 pb-4">
            {filtered.map(conv => {
              const isActive = activeConversationId === conv.conversation_id;
              const lastMsg = conv.messages && conv.messages.length > 0 ? conv.messages[conv.messages.length - 1].content : null;
              return (
                <div 
                  key={conv.conversation_id}
                  onClick={() => onSelectConversation(conv.conversation_id)}
                  className={`group relative flex flex-col p-3 rounded-xl cursor-pointer transition-all duration-200 border ${
                    isActive 
                      ? 'bg-secondary border-border/50 shadow-sm' 
                      : 'bg-transparent border-transparent hover:bg-secondary/40'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2 w-full mb-1">
                    {editingId === conv.conversation_id ? (
                      <input
                        autoFocus
                        value={editTitle}
                        onChange={e => setEditTitle(e.target.value)}
                        onBlur={() => submitRename(conv.conversation_id)}
                        onKeyDown={e => e.key === 'Enter' && submitRename(conv.conversation_id)}
                        className="flex-1 bg-background text-sm font-medium border border-ring rounded px-1.5 py-0.5 outline-none w-full"
                        onClick={e => e.stopPropagation()}
                      />
                    ) : (
                      <span className={`text-sm font-medium truncate flex-1 transition-colors ${isActive ? 'text-foreground' : 'text-foreground/80 group-hover:text-foreground'}`}>
                        {conv.title}
                      </span>
                    )}
                    
                    {!editingId && (
                      <span className="text-[10px] text-muted-foreground font-mono shrink-0 pt-0.5">
                        {formatTimeAgo(conv.updated_at)}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex justify-between items-center w-full">
                    <span className="text-xs text-muted-foreground truncate flex-1 pr-4">
                      {lastMsg || "View conversation..."}
                    </span>
                    
                    <div className={`flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-gradient-to-l from-secondary via-secondary to-transparent pl-4 absolute right-2 bottom-2 ${
                      isActive ? 'from-secondary' : 'from-card'
                    }`}>
                      <button onClick={(e) => startRename(conv.conversation_id, conv.title, e)} className="p-1.5 bg-background rounded-md text-muted-foreground hover:text-foreground shadow-sm">
                        <Edit2 size={12} />
                      </button>
                      <button onClick={(e) => handleDelete(conv.conversation_id, e)} className="p-1.5 bg-background rounded-md text-muted-foreground hover:text-destructive shadow-sm">
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      
      {/* Developer Diagnostics Toggle (Development Mode Only) */}
      <div className="p-3 border-t border-border/40">
        <button 
          onClick={() => setShowDiagnostics(!showDiagnostics)}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground w-full p-2 rounded-lg hover:bg-secondary transition-colors"
        >
          <Settings2 size={14} />
          System Status
        </button>
      </div>

      {/* Diagnostics Panel Modal/Overlay */}
      <AnimatePresence>
        {showDiagnostics && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-16 left-3 w-64 bg-card border border-border shadow-2xl rounded-xl p-4 z-50"
          >
            <h4 className="text-xs font-bold uppercase tracking-wider mb-3 text-muted-foreground">Diagnostics</h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between"><span className="opacity-70">Provider</span><span>OpenRouter</span></div>
              <div className="flex justify-between"><span className="opacity-70">Model</span><span className="truncate w-32 text-right">Nemotron 3</span></div>
              <div className="flex justify-between"><span className="opacity-70">Safety</span><span className="text-emerald-400">Deterministic</span></div>
              <div className="flex justify-between"><span className="opacity-70">Active Conv</span><span className="truncate w-24 text-right font-mono">{activeConversationId ? activeConversationId.slice(0, 8) + '...' : 'None'}</span></div>
            </div>
            <button onClick={() => setShowDiagnostics(false)} className="mt-4 w-full bg-secondary text-foreground py-1.5 rounded hover:bg-secondary/80">Close</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
