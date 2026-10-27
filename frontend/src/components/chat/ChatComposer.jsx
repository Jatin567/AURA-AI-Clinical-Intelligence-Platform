import React, { useState, useRef, useEffect } from 'react';
import { useSessionEngine } from '../../engine/SessionEngine';
import { Paperclip, Mic, StopCircle, ArrowUp } from 'lucide-react';
import { uploadArtifact } from '../../services/api';

export const ChatComposer = ({ activeConversationId, onEnsureConversation, onSendMessage, onStopGeneration }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);
  const { conversationState } = useSessionEngine();
  
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const recognitionRef = useRef(null);
  const baseMessageRef = useRef('');
  const wantRecordingRef = useRef(false);

  const isGenerating = conversationState.status === 'generating';

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  // Clean up recognition on unmount
  useEffect(() => {
    return () => {
      wantRecordingRef.current = false;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
        recognitionRef.current = null;
      }
    };
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (message.trim()) {
        onSendMessage(message);
        setMessage('');
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileUpload(file);
  };
  
  const handleFileUpload = async (file) => {
    try {
      const conversationId = onEnsureConversation
        ? await onEnsureConversation(file.name)
        : activeConversationId;
      if (!conversationId) {
        alert("Unable to start a conversation for this upload.");
        return;
      }

      setIsUploading(true);
      setUploadProgress(0);

      await uploadArtifact(conversationId, file, (percent) => {
        setUploadProgress(percent);
      });
      onSendMessage(`Uploaded artifact: ${file.name}`);
    } catch (err) {
      alert("Upload error: " + err.message);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleFileUpload(file);
  };

  const stopRecording = () => {
    wantRecordingRef.current = false;
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // Already stopped
      }
      recognitionRef.current = null;
    }
    setIsRecording(false);
  };

  const toggleRecording = (event) => {
    event?.preventDefault?.();
    event?.stopPropagation?.();

    if (wantRecordingRef.current || isRecording) {
      stopRecording();
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Apple Safari.');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = navigator.language || 'en-US';
      recognitionRef.current = recognition;
      wantRecordingRef.current = true;
      baseMessageRef.current = message.trim();
      setRecordingTime(0);

      recognition.onstart = () => {
        setIsRecording(true);
      };

      recognition.onresult = (e) => {
        let interimText = '';
        let finalText = '';
        for (let i = 0; i < e.results.length; i++) {
          const item = e.results[i];
          if (item.isFinal) {
            finalText += (finalText ? ' ' : '') + item[0].transcript.trim();
          } else {
            interimText += (interimText ? ' ' : '') + item[0].transcript.trim();
          }
        }
        const combined = [finalText, interimText].filter(Boolean).join(' ').trim();
        if (combined) {
          const base = baseMessageRef.current;
          setMessage(base ? `${base} ${combined}` : combined);
        }
      };

      recognition.onerror = (e) => {
        if (e.error === 'no-speech' || e.error === 'aborted') {
          // Non-fatal: brief silence or abort should not crash the session
          return;
        }
        if (e.error === 'not-allowed' || e.error === 'permission-denied') {
          alert('Microphone access was denied. Please allow microphone permissions in your browser settings.');
        } else if (e.error === 'audio-capture') {
          alert('No microphone was detected on your device.');
        } else if (e.error === 'network') {
          alert('Network error occurred during speech recognition. Please check your internet connection.');
        } else {
          console.warn('SpeechRecognition error:', e.error);
        }
        stopRecording();
      };

      recognition.onend = () => {
        if (wantRecordingRef.current) {
          // If browser closed the session on a natural pause, update the base message and restart
          baseMessageRef.current = textareaRef.current?.value || message;
          try {
            recognition.start();
            return;
          } catch {
            // Restart failed, stop gracefully
          }
        }
        setIsRecording(false);
        wantRecordingRef.current = false;
        recognitionRef.current = null;
      };

      recognition.start();
    } catch (err) {
      console.error('Failed to start SpeechRecognition:', err);
      alert('Could not start voice recognition: ' + (err.message || 'unknown error'));
      stopRecording();
    }
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="w-full flex flex-col items-center justify-center p-4">
      {isGenerating && (
        <button 
          onClick={onStopGeneration}
          className="mb-6 flex items-center gap-2 px-5 py-2.5 rounded-full bg-secondary text-foreground hover:bg-secondary/80 border border-border/50 text-sm font-medium transition-all shadow-md hover:shadow-lg backdrop-blur-md"
        >
          <StopCircle size={16} className="text-muted-foreground" />
          Stop generating
        </button>
      )}
      
      <div 
        className="glass-input w-full max-w-3xl rounded-[24px] p-4 shadow-2xl relative flex flex-col transition-all duration-300 bg-card/80 border border-border/60 hover:border-border"
        onDrop={handleDrop} 
        onDragOver={(e) => e.preventDefault()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept=".pdf,.png,.jpg,.jpeg" 
          onChange={handleFileChange}
        />
        
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your symptoms or upload a report..."
          className="w-full bg-transparent border-none text-foreground text-[16px] resize-none focus:outline-none focus:ring-0 placeholder:text-muted-foreground/70 px-2 py-2 max-h-[200px] overflow-y-auto custom-scrollbar leading-relaxed"
          rows={1}
          disabled={isGenerating || isUploading}
        />
        
        <div className="flex justify-between items-center px-1 pt-3 mt-1">
          <div className="flex items-center gap-1 text-muted-foreground">
            <button 
              className={`p-2.5 rounded-full transition-all group ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'hover:bg-secondary hover:text-foreground'}`}
              title="Attach File"
              aria-label="Attach File"
              disabled={isGenerating}
              onClick={() => fileInputRef.current?.click()}
            >
              <Paperclip size={20} className={!isGenerating ? "group-hover:scale-110 transition-transform" : ""} />
            </button>
            <button 
              type="button"
              className={`p-2.5 rounded-full transition-all group ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'hover:bg-secondary hover:text-foreground'} ${isRecording ? 'bg-destructive/15 text-destructive ring-2 ring-destructive/30 animate-pulse' : ''}`} 
              title={isRecording ? "Stop Listening" : "Voice Input"}
              aria-label={isRecording ? "Stop Listening" : "Voice Input"}
              disabled={isGenerating}
              onClick={toggleRecording}
            >
              <Mic size={20} className={!isGenerating ? "group-hover:scale-110 transition-transform" : ""} />
            </button>
            
            {isUploading && (
              <span className="ml-3 text-xs font-medium text-accent animate-pulse">
                Uploading... {uploadProgress}%
              </span>
            )}

            {isRecording && !isUploading && (
              <span className="ml-3 text-xs font-medium text-destructive flex items-center gap-1.5 animate-pulse">
                <span className="w-2 h-2 rounded-full bg-destructive"></span>
                Listening... {formatTime(recordingTime)}
              </span>
            )}
            
            {message.length > 0 && !isUploading && !isRecording && (
              <span className="ml-3 text-xs font-mono text-muted-foreground/50">
                {message.length} chars
              </span>
            )}
          </div>
          
          <button 
            className={`p-3 rounded-full flex items-center justify-center transition-all duration-300 ${
              message.trim() && !isGenerating 
                ? 'bg-foreground text-background shadow-lg shadow-foreground/20 hover:scale-105' 
                : 'bg-secondary/80 text-muted-foreground/50 cursor-not-allowed'
            }`}
            onClick={() => {
              if (message.trim() && !isGenerating) {
                onSendMessage(message);
                setMessage('');
              }
            }}
            disabled={!message.trim() || isGenerating}
            aria-label="Send Message"
          >
            <ArrowUp size={20} strokeWidth={2.5} />
          </button>
        </div>
      </div>
      <div className="text-center mt-4 text-[11px] font-medium text-muted-foreground/50 tracking-wide">
        AURA AI Health OS. Information is for demonstration purposes.
      </div>
    </div>
  );
};
