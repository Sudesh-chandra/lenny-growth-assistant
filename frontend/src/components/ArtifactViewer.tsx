import { useState, useMemo } from 'react';
import {
  X, Eye, Code, Copy, Check, Download, Maximize2,
  Monitor, Tablet, Smartphone, FileCode, FileText, Sparkles
} from 'lucide-react';
import DOMPurify from 'dompurify';
import ReactMarkdown from 'react-markdown';
import type { Artifact } from '../lib/types';

interface ArtifactViewerProps {
  artifact: Artifact;
  onClose: () => void;
}

type ViewportMode = 'desktop' | 'tablet' | 'mobile';

const VIEWPORT_WIDTHS: Record<ViewportMode, string> = {
  desktop: '100%',
  tablet: '768px',
  mobile: '375px',
};

export default function ArtifactViewer({ artifact, onClose }: ArtifactViewerProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);
  const [viewport, setViewport] = useState<ViewportMode>('desktop');

  const sanitizedHtml = useMemo(() => {
    if (artifact.artifact_type !== 'html') return '';
    return DOMPurify.sanitize(artifact.content, {
      USE_PROFILES: { html: true },
      ADD_TAGS: ['style'],
      ADD_ATTR: ['target'],
      ALLOW_UNKNOWN_PROTOCOLS: false,
      WHOLE_DOCUMENT: true,
      RETURN_TRUSTED_TYPE: false,
    });
  }, [artifact.content]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = artifact.content;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === 'html' ? 'html' : 'md';
    const mime = artifact.artifact_type === 'html' ? 'text/html' : 'text/markdown';
    const blob = new Blob([artifact.content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/\s+/g, '_').toLowerCase()}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePopout = () => {
    if (artifact.artifact_type === 'html') {
      const win = window.open('', '_blank');
      if (win) {
        win.document.write(sanitizedHtml);
        win.document.close();
      }
    }
  };

  return (
    <div className="w-[50%] border-l border-white/[0.06] flex flex-col animate-slide-in" style={{ background: 'linear-gradient(180deg, #0f172a 0%, #090d16 100%)' }}>
      {/* Header / Toolbar */}
      <div className="px-4 py-3 border-b border-white/[0.06]">
        {/* Title Row */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-accent-indigo/15 flex items-center justify-center shrink-0">
              {artifact.artifact_type === 'html' ? (
                <FileCode size={14} className="text-accent-indigo" />
              ) : (
                <FileText size={14} className="text-accent-violet" />
              )}
            </div>
            <div className="min-w-0">
              <h3 className="text-sm font-semibold text-slate-200 truncate font-display">
                {artifact.title}
              </h3>
              <div className="flex items-center gap-1.5 mt-0.5">
                <Sparkles size={9} className="text-accent-indigo" />
                <span className="text-[10px] text-slate-500">
                  {artifact.artifact_type === 'html' ? 'HTML / CSS Component' : 'Markdown Document'} • Sandboxed
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-slate-300 hover:bg-white/[0.06] rounded-lg transition-all"
          >
            <X size={15} />
          </button>
        </div>

        {/* Controls Row */}
        <div className="flex items-center justify-between">
          {/* Tab Toggle */}
          <div className="flex bg-white/[0.04] rounded-lg p-0.5 border border-white/[0.06]">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[11px] font-medium transition-all duration-200 ${
                activeTab === 'preview'
                  ? 'bg-accent-indigo/15 text-accent-indigo border border-accent-indigo/20'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Eye size={12} />
              Preview
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[11px] font-medium transition-all duration-200 ${
                activeTab === 'code'
                  ? 'bg-accent-indigo/15 text-accent-indigo border border-accent-indigo/20'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Code size={12} />
              Code
            </button>
          </div>

          {/* Viewport Toggles (only in preview mode) */}
          {activeTab === 'preview' && artifact.artifact_type === 'html' && (
            <div className="flex items-center gap-0.5 bg-white/[0.03] rounded-lg p-0.5 border border-white/[0.04]">
              {([
                { mode: 'desktop' as ViewportMode, icon: Monitor, label: 'Desktop' },
                { mode: 'tablet' as ViewportMode, icon: Tablet, label: 'Tablet' },
                { mode: 'mobile' as ViewportMode, icon: Smartphone, label: 'Mobile' },
              ]).map(({ mode, icon: Icon, label }) => (
                <button
                  key={mode}
                  onClick={() => setViewport(mode)}
                  className={`p-1.5 rounded-md transition-all ${
                    viewport === mode
                      ? 'bg-white/[0.08] text-slate-200'
                      : 'text-slate-600 hover:text-slate-400'
                  }`}
                  title={label}
                >
                  <Icon size={13} />
                </button>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-1">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] rounded-lg transition-all"
              title="Copy code"
            >
              {copied ? <Check size={12} className="text-accent-emerald" /> : <Copy size={12} />}
              <span className="hidden sm:inline">{copied ? 'Copied!' : 'Copy'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] rounded-lg transition-all"
              title="Download"
            >
              <Download size={12} />
              <span className="hidden sm:inline">Download</span>
            </button>
            {artifact.artifact_type === 'html' && (
              <button
                onClick={handlePopout}
                className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] rounded-lg transition-all"
                title="Popout to new tab"
              >
                <Maximize2 size={12} />
                <span className="hidden sm:inline">Popout</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto relative">
        {activeTab === 'preview' ? (
          artifact.artifact_type === 'html' ? (
            <div className="w-full h-full flex items-start justify-center bg-white/[0.02] p-0">
              <iframe
                srcDoc={sanitizedHtml}
                className="h-full border-0 bg-white transition-all duration-300"
                style={{ width: VIEWPORT_WIDTHS[viewport] }}
                sandbox="allow-scripts"
                title="Artifact Preview"
              />
            </div>
          ) : (
            <div className="p-6 markdown-content max-w-2xl mx-auto">
              <ReactMarkdown>{artifact.content}</ReactMarkdown>
            </div>
          )
        ) : (
          /* Code View */
          <div className="p-4">
            <pre className="bg-surface-0 border border-white/[0.06] text-slate-300 p-5 rounded-xl overflow-auto text-[13px] leading-relaxed font-mono">
              <code>{artifact.content}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
