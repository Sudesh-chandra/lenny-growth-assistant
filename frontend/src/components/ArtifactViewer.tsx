import { useState, useMemo } from 'react';
import { X, Eye, Code, Copy, Check } from 'lucide-react';
import DOMPurify from 'dompurify';
import ReactMarkdown from 'react-markdown';
import type { Artifact } from '../lib/types';

interface ArtifactViewerProps {
  artifact: Artifact;
  onClose: () => void;
}

export default function ArtifactViewer({ artifact, onClose }: ArtifactViewerProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  // Sanitize HTML for safe rendering
  const sanitizedHtml = useMemo(() => {
    if (artifact.artifact_type !== 'html') return '';
    
    // Use DOMPurify with strict settings
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
      // Fallback
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

  return (
    <div className="w-[50%] border-l border-slate-200 bg-white flex flex-col animate-slide-in">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-slate-700 truncate max-w-[200px]">
            {artifact.title}
          </h3>
          <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full uppercase">
            {artifact.artifact_type}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Tab Toggle */}
          <div className="flex bg-slate-100 rounded-lg p-0.5">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeTab === 'preview'
                  ? 'bg-white text-slate-700 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Eye size={12} />
              Preview
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeTab === 'code'
                  ? 'bg-white text-slate-700 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Code size={12} />
              Code
            </button>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="p-2 text-slate-400 hover:text-slate-600 transition-colors"
            title="Copy code"
          >
            {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'preview' ? (
          artifact.artifact_type === 'html' ? (
            // Sandboxed iframe for HTML artifacts
            <iframe
              srcDoc={sanitizedHtml}
              className="w-full h-full border-0"
              sandbox="allow-scripts"
              title="Artifact Preview"
            />
          ) : (
            // Markdown preview
            <div className="p-6 markdown-content">
              <ReactMarkdown>{artifact.content}</ReactMarkdown>
            </div>
          )
        ) : (
          // Code view
          <div className="p-4">
            <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-auto text-sm leading-relaxed">
              <code>{artifact.content}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
