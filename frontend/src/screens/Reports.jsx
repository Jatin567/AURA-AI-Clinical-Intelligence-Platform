import React, { useState, useEffect, useCallback } from 'react';
import { PageTransition } from '../components/PageTransition';
import { useAuth } from '../context/AuthContext';
import { FileText, Download, Printer, AlertCircle, RefreshCw, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE } from '../services/api';

export default function Reports() {
  const { user } = useAuth();
  const patientId = user?.[0]?.patient_id || 'default_patient';

  const [markdown, setMarkdown] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const fetchReport = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('aura_token');
      const res = await fetch(`${API_BASE}/export/markdown?patient_id=${patientId}`, {
        headers: {
          ...(token && { Authorization: `Bearer ${token}` })
        }
      });
      if (!res.ok) {
        throw new Error('Failed to generate clinical report');
      }
      const text = await res.text();
      setMarkdown(text);
    } catch (err) {
      setError(err.message || 'Error fetching report');
    } finally {
      setIsLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  const handleDownloadPdf = () => {
    const token = localStorage.getItem('aura_token');
    const url = `${API_BASE}/export/pdf?patient_id=${patientId}`;
    fetch(url, {
      headers: { ...(token && { Authorization: `Bearer ${token}` }) }
    })
      .then(res => res.blob())
      .then(blob => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `aura_report_${patientId}.pdf`;
        link.click();
      })
      .catch(err => alert('PDF export failed: ' + err.message));
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `aura_report_${patientId}.md`;
    link.click();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const hasContent = markdown && !markdown.includes('No assessments recorded yet');

  return (
    <PageTransition>
      <div className="flex h-full w-full bg-background text-foreground flex-col overflow-hidden">
        {/* Header */}
        <header className="px-8 pt-8 pb-6 border-b border-border shrink-0 bg-background flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono uppercase tracking-widest text-primary font-semibold">Documentation</span>
            </div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight mt-1">Clinical Reports</h1>
            <p className="text-xs text-muted-foreground mt-0.5">
              Truthful deterministic clinical summaries generated from verified intake & assessments.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={fetchReport}
              disabled={isLoading}
              className="p-2 bg-secondary text-muted-foreground hover:text-foreground rounded-lg border border-border transition-colors"
              title="Refresh"
            >
              <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            </button>
            <button
              onClick={handleDownloadMarkdown}
              disabled={isLoading || !markdown}
              className="flex items-center gap-2 px-3 py-2 bg-secondary hover:bg-secondary/80 text-foreground text-xs font-medium rounded-lg border border-border transition-colors"
            >
              <Download size={14} />
              Markdown
            </button>
            <button
              onClick={handleDownloadPdf}
              disabled={isLoading || !markdown}
              className="flex items-center gap-2 px-3 py-2 bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-medium rounded-lg shadow-sm transition-colors"
            >
              <FileText size={14} />
              Download PDF
            </button>
            <button
              onClick={() => window.print()}
              disabled={isLoading || !markdown}
              className="flex items-center gap-2 px-3 py-2 bg-secondary hover:bg-secondary/80 text-foreground text-xs font-medium rounded-lg border border-border transition-colors"
            >
              <Printer size={14} />
              Print
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          <div className="max-w-4xl mx-auto">
            {isLoading && (
              <div className="space-y-4">
                <div className="h-8 bg-secondary/50 rounded-lg animate-pulse w-1/3"></div>
                <div className="h-32 bg-secondary/30 rounded-xl animate-pulse"></div>
                <div className="h-48 bg-secondary/30 rounded-xl animate-pulse"></div>
              </div>
            )}

            {error && (
              <div className="p-6 bg-destructive/10 border border-destructive/20 rounded-xl text-center">
                <AlertCircle className="mx-auto text-destructive mb-2" size={28} />
                <h3 className="font-semibold text-foreground">Unable to load report</h3>
                <p className="text-xs text-muted-foreground mt-1 mb-4">{error}</p>
                <button
                  onClick={fetchReport}
                  className="px-4 py-2 bg-secondary text-foreground text-xs rounded-lg border border-border hover:bg-secondary/80"
                >
                  Retry
                </button>
              </div>
            )}

            {!isLoading && !error && !hasContent && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8">
                <div className="bg-card border border-dashed border-border rounded-2xl p-12 flex flex-col items-center justify-center text-center shadow-sm">
                  <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mb-6 border border-border/50">
                    <FileText className="text-muted-foreground" size={28} />
                  </div>
                  <h3 className="text-xl font-semibold text-foreground mb-2">No Reports Generated Yet</h3>
                  <p className="text-sm text-muted-foreground max-w-md mb-6 leading-relaxed">
                    Clinical reports and discharge summaries are synthesized deterministically after a patient intake session or health assessment is completed.
                  </p>
                </div>
              </motion.div>
            )}

            {!isLoading && !error && hasContent && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div className="flex justify-between items-center bg-card/60 backdrop-blur-sm px-5 py-3 border border-border rounded-xl">
                  <span className="text-xs font-mono text-muted-foreground">Document Format: CommonMark / PDF 1.4</span>
                  <button
                    onClick={handleCopy}
                    className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1.5 transition-colors"
                  >
                    {copied ? <CheckCircle2 size={14} className="text-emerald-400" /> : null}
                    {copied ? 'Copied' : 'Copy Raw Markdown'}
                  </button>
                </div>

                <div className="bg-card border border-border rounded-2xl p-8 shadow-sm prose prose-invert max-w-none text-foreground prose-headings:text-foreground prose-p:text-muted-foreground prose-strong:text-foreground prose-li:text-muted-foreground">
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed bg-transparent p-0 border-0 m-0">
                    {markdown}
                  </pre>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
