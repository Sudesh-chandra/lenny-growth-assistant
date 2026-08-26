import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { FileCode, FileText, ExternalLink, ChevronDown, ChevronUp, User } from 'lucide-react';
import { LennyAvatar, PodcastSourceIcon } from './ProviderLogos';
import type { Message, Citation } from '../lib/types';

interface MessageBubbleProps {
  message: Message;
  onOpenArtifact?: () => void;
  artifactTitle?: string;
}

function SourceChip({ citation, index }: { citation: Citation; index: number }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="inline-block">
      <button
        onClick={() => setExpanded(!expanded)}
        className="source-chip"
      >
        <span className="w-4 h-4 rounded-full bg-accent-indigo/20 flex items-center justify-center text-[9px] font-bold text-accent-indigo">
          {index + 1}
        </span>
        <span className="truncate max-w-[120px]">
          {citation.guest || citation.source}
        </span>
        {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
      </button>

      {expanded && (
        <div className="absolute z-40 mt-1 w-72 glass rounded-xl p-3 shadow-glass animate-fade-in">
          <div className="flex items-start gap-2">
            <div className="w-6 h-6 rounded-full bg-accent-indigo/20 flex items-center justify-center shrink-0 mt-0.5">
              <PodcastSourceIcon size={14} />
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-semibold text-slate-200 truncate">
                {citation.guest || 'Unknown Guest'}
              </p>
              <p className="text-[10px] text-slate-500 truncate">{citation.source}</p>
              {citation.text_snippet && (
                <p className="text-[11px] text-slate-400 mt-1.5 line-clamp-3 italic leading-relaxed">
                  "{citation.text_snippet}"
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function MessageBubble({ message, onOpenArtifact, artifactTitle }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition-all ${
          isUser
            ? 'bg-gradient-to-br from-slate-600 to-slate-700 shadow-sm'
            : 'bg-gradient-to-br from-accent-indigo/20 to-accent-violet/20 border border-accent-indigo/20'
        }`}
      >
        {isUser ? (
          <User size={13} className="text-slate-300" />
        ) : (
          <LennyAvatar size={28} />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 min-w-0 ${isUser ? 'flex flex-col items-end' : ''}`}>
        {/* Message Bubble */}
        <div
          className={`inline-block rounded-2xl px-4 py-3 max-w-full text-left transition-all ${
            isUser
              ? 'bg-gradient-to-br from-accent-indigo/90 to-accent-violet/90 text-white rounded-tr-sm shadow-glow-sm'
              : 'bg-white/[0.04] rounded-tl-sm border border-white/[0.06]'
          }`}
        >
          <div className={`markdown-content text-[13px] leading-relaxed ${isUser ? 'text-white/90' : 'text-slate-300'}`}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {/* Interactive Artifact Card (replaces raw code in chat) */}
        {!isUser && message.has_artifact && (
          <button
            onClick={onOpenArtifact}
            className="artifact-card mt-3 w-full max-w-md text-left group"
          >
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-accent-indigo/15 flex items-center justify-center shrink-0 group-hover:bg-accent-indigo/25 transition-colors">
                {message.has_artifact === 'html' ? (
                  <FileCode size={16} className="text-accent-indigo" />
                ) : (
                  <FileText size={16} className="text-accent-violet" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-semibold text-accent-indigo uppercase tracking-wider">
                    Interactive Artifact
                  </span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-accent-indigo/10 text-accent-indigo/70 border border-accent-indigo/10">
                    {message.has_artifact === 'html' ? 'HTML/CSS' : 'Markdown'}
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-200 mt-1 truncate">
                  {artifactTitle || 'Generated Artifact'}
                </p>
                <div className="flex items-center gap-3 mt-2">
                  <span className="flex items-center gap-1 text-[11px] text-accent-indigo font-medium">
                    <ExternalLink size={11} />
                    Open in Viewer
                  </span>
                </div>
              </div>
            </div>
          </button>
        )}

        {/* Source Citation Chips */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2.5 relative">
            {message.citations.map((citation, i) => (
              <SourceChip key={i} citation={citation} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
