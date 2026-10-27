import React from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatMessage = ({ msg }) => {
  const isUser = msg.role === 'user';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {isUser ? (
        <div className="group relative bg-accent text-accent-foreground px-5 py-3.5 rounded-[24px] rounded-tr-sm max-w-[70%] shadow-sm bg-gradient-to-br from-accent to-accent/90">
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
          <span className="absolute -bottom-5 right-1 text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity font-mono">
            Just now
          </span>
        </div>
      ) : (
        <div className="flex gap-4 w-full">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-emerald-400 shrink-0 flex items-center justify-center mt-1 shadow-md">
            <Activity size={16} className="text-white" />
          </div>
          <div className="text-[15px] leading-relaxed text-foreground mt-1.5 flex-1 prose prose-invert prose-p:leading-relaxed prose-pre:bg-secondary prose-pre:border prose-pre:border-border prose-a:text-accent">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.content}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ChatMessage;
