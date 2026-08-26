import ReactMarkdown from 'react-markdown';
import { FileCode, FileText } from 'lucide-react';
import type { Message } from '../lib/types';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''} animate-fade-in`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? 'bg-slate-700 text-white' : 'bg-primary-100'
        }`}
      >
        {isUser ? (
          <span className="text-xs font-bold">U</span>
        ) : (
          <span className="text-sm">🤖</span>
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 min-w-0 ${isUser ? 'text-right' : ''}`}>
        <div
          className={`inline-block rounded-2xl px-4 py-3 max-w-full text-left ${
            isUser
              ? 'bg-primary-600 text-white rounded-tr-sm'
              : 'bg-white rounded-tl-sm shadow-sm border border-slate-100'
          }`}
        >
          <div className={`markdown-content text-sm ${isUser ? 'text-white' : 'text-slate-700'}`}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {/* Citations */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {message.citations.map((citation, i) => (
              <span
                key={i}
                className="citation-badge"
                title={`${citation.source}${citation.guest ? ` - ${citation.guest}` : ''}\n${citation.text_snippet || ''}`}
              >
                [Source {i + 1}] {citation.source}
                {citation.guest && ` - ${citation.guest}`}
              </span>
            ))}
          </div>
        )}

        {/* Artifact indicator */}
        {!isUser && message.has_artifact && (
          <div className="flex items-center gap-1 mt-2 text-xs text-primary-600">
            {message.has_artifact === 'html' ? (
              <FileCode size={12} />
            ) : (
              <FileText size={12} />
            )}
            <span>Artifact generated — view in panel →</span>
          </div>
        )}
      </div>
    </div>
  );
}
