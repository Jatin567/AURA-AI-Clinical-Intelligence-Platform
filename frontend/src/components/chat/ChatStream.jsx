import React, { useEffect, useState, useRef } from 'react';
import { CardRenderer } from '../../engine/CardRenderer';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, CheckCircle2, AlertCircle } from 'lucide-react';
import ChatMessage from '../ChatMessage';

const inflightStreams = new Set();

export const ChatStream = ({ conversationId, triggerStream, userMessages = [], onStreamEnd }) => {
  const [items, setItems] = useState([]);
  const [tools, setTools] = useState([]);
  const [status, setStatus] = useState('idle');
  const bottomRef = useRef(null);
  const abortControllerRef = useRef(null);
  const onStreamEndRef = useRef(onStreamEnd);

  useEffect(() => {
    onStreamEndRef.current = onStreamEnd;
  }, [onStreamEnd]);

  useEffect(() => {
    if (!triggerStream || !conversationId) return;

    const key = `${conversationId}::${triggerStream}`;
    if (inflightStreams.has(key)) return;

    inflightStreams.add(key);
    const controller = new AbortController();
    abortControllerRef.current = controller;
    let finished = false;

    const finish = () => {
      if (finished) return;
      finished = true;
      inflightStreams.delete(key);
      onStreamEndRef.current?.();
    };

    const handleEvent = (event, data) => {
      if (event === 'TEXT_CHUNK') {
        const textContent = (data && typeof data.text === 'string') ? data.text : (typeof data === 'string' ? data : '');
        if (!textContent) return;
        setItems(prev => {
          const last = prev[prev.length - 1];
          if (last && last.type === 'text') {
            return [...prev.slice(0, -1), { ...last, content: last.content + textContent }];
          }
          return [...prev, { type: 'text', content: textContent, id: Date.now() + Math.random() }];
        });
      } else if (event === 'CARD') {
        setItems(prev => [...prev, { type: 'card', manifest: data.manifest || data, id: Date.now() + Math.random() }]);
      } else if (event === 'STATUS') {
        setStatus(data.status || 'generating');
      } else if (event === 'TOOL_START') {
        setTools(prev => [...prev, { id: data.tool, message: data.message, status: 'running' }]);
      } else if (event === 'TOOL_END') {
        setTools(prev => prev.map(t => t.id === data.tool ? { ...t, status: 'completed' } : t));
      } else if (event === 'COMPLETE') {
        setStatus('done');
      } else if (event === 'ERROR') {
        setStatus('error');
        const text = (data && data.message) ? data.message : 'An error occurred while generating the response.';
        setItems(prev => [...prev, { type: 'text', content: text, id: Date.now() + Math.random() }]);
      }
    };

    const startStream = async () => {
      setItems([]);
      setTools([]);
      setStatus('generating');

      try {
        const token = localStorage.getItem('aura_token');
        const response = await fetch(`/api/chat/conversations/${conversationId}/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
          },
          body: JSON.stringify({ content: triggerStream, patient_id: 'default' }),
          signal: controller.signal
        });

        if (!response.ok) throw new Error("Stream failed to start");

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let currentEvent = 'message';

        while (true) {
          const { value, done } = await reader.read();
          if (done) {
            setStatus((prev) => (prev === 'generating' ? 'done' : prev));
            finish();
            break;
          }
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop(); 

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEvent = line.replace('event:', '').trim();
            } else if (line.startsWith('data:')) {
              const dataStr = line.replace('data:', '').trim();
              if (dataStr) {
                try {
                  const data = JSON.parse(dataStr);
                  handleEvent(currentEvent, data);
                } catch {
                  // Ignore parse errors on partial chunks
                }
              }
            }
          }
        }
      } catch (err) {
        if (err.name === 'AbortError') {
          setStatus('interrupted');
        } else {
          console.error("Stream error:", err);
          setStatus('error');
          setItems(prev => [...prev, {
            type: 'text',
            content: 'I could not generate a reply just then. Please try sending your message again.',
            id: Date.now() + Math.random()
          }]);
        }
        finish();
      }
    };

    startStream();

    return () => {
      // Do not abort on unmount — React Strict Mode remounts would drop the reply.
    };
  }, [triggerStream, conversationId]);

  useEffect(() => {
    const isNearBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 200;
    if (isNearBottom) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [items, userMessages, tools]);

  useEffect(() => {
    window.abortCurrentStream = () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
    return () => { delete window.abortCurrentStream; };
  }, []);

  const visibleMessages = userMessages.filter((msg, index, list) => {
    if (index === 0) return true;
    const prev = list[index - 1];
    return !(prev.role === msg.role && prev.content === msg.content);
  });

  const thread = [...visibleMessages];
  const lastUser = [...thread].reverse().find((m) => m.role === 'user');
  if (triggerStream && (!lastUser || lastUser.content !== triggerStream)) {
    thread.push({ role: 'user', content: triggerStream, message_id: 'pending-user' });
  }

  const streamedText = items.filter((item) => item.type === 'text').map((item) => item.content).join('');
  const lastThread = thread[thread.length - 1];
  const streamAlreadyInThread = Boolean(
    streamedText && lastThread?.role === 'assistant' && lastThread.content === streamedText
  );
  const showLiveStream = !streamAlreadyInThread && (status === 'generating' || items.length > 0 || tools.length > 0);

  return (
    <div className="flex flex-col gap-6 max-w-[900px] mx-auto w-full pb-10 pt-6 px-4 md:px-0">
      <AnimatePresence initial={false}>
        {thread.map((msg, idx) => (
          <ChatMessage key={msg.message_id || msg.id || `${msg.role}-${idx}`} msg={msg} />
        ))}

        {showLiveStream && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-4 w-full justify-start mt-2"
          >
            {items.length === 0 && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-emerald-400 shrink-0 flex items-center justify-center mt-1 shadow-md">
                <Activity size={16} className="text-white" />
              </div>
            )}
            <div className={`flex flex-col gap-4 flex-1 text-[15px] leading-relaxed text-foreground mt-1.5 ${items.length > 0 ? '' : ''}`}>
              
              {/* Tool Timeline */}
              {tools.length > 0 && (
                <div className="flex flex-col gap-2 mb-2">
                  {tools.map(tool => (
                    <div key={tool.id} className="flex items-center gap-2 text-sm text-muted-foreground bg-secondary/30 p-2 rounded-lg w-fit">
                      {tool.status === 'running' ? (
                        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                          <Activity size={14} />
                        </motion.div>
                      ) : (
                        <CheckCircle2 size={14} className="text-emerald-500" />
                      )}
                      <span>{tool.message}</span>
                      {tool.status === 'completed' && <span className="ml-2 text-emerald-600 font-medium text-xs">✓ Completed</span>}
                    </div>
                  ))}
                </div>
              )}

              {/* Generated Content */}
              {items.map((item) => {
                if (item.type === 'text') {
                  // We treat the current streaming text as an assistant message
                  return <ChatMessage key={item.id} msg={{ role: 'assistant', content: item.content }} />;
                } else if (item.type === 'card') {
                  return (
                    <motion.div 
                      key={item.id}
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ type: "spring", stiffness: 400, damping: 25 }}
                      className="w-full pl-[48px]"
                    >
                      <CardRenderer manifest={item.manifest} />
                    </motion.div>
                  );
                }
                return null;
              })}
              
              {/* Typing Indicator */}
              {status === 'generating' && (
                <div className="flex items-center gap-1.5 h-6 px-1 mt-2">
                  <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 bg-muted-foreground rounded-full" />
                  <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-muted-foreground rounded-full" />
                  <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-muted-foreground rounded-full" />
                </div>
              )}
              
              {status === 'error' && (
                <div className="flex items-center gap-2 text-red-500 text-sm mt-2">
                  <AlertCircle size={16} />
                  <span>An error occurred while generating the response.</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <div ref={bottomRef} className="h-4" />
    </div>
  );
};
