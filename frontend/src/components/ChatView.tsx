import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import type { Message, Citation } from '../lib/types';
import MessageBubble from './MessageBubble';

interface ChatViewProps {
  messages: Message[];
  streamingContent: string;
  streamingCitations: Citation[];
  isStreaming: boolean;
  onSendMessage: (content: string) => void;
  sessionTitle: string;
}

export default function ChatView({
  messages,
  streamingContent,
  streamingCitations,
  isStreaming,
  onSendMessage,
  sessionTitle,
}: ChatViewProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 py-3 border-b border-slate-200 bg-white">
        <h2 className="text-sm font-semibold text-slate-700 truncate">{sessionTitle}</h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && !streamingContent && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-5xl mb-4">🚀</div>
            <h3 className="text-xl font-bold text-slate-700 mb-2">
              Lenny Growth Assistant
            </h3>
            <p className="text-sm text-slate-500 max-w-md mb-6">
              Ask product management and growth questions grounded in Lenny's Podcast transcripts.
              Generate content, essays, and interactive artifacts.
            </p>
            <div className="grid grid-cols-2 gap-3 max-w-lg">
              {[
                'What is product-led growth?',
                'How do growth loops work?',
                'Write an essay about user activation',
                'Create a pricing dashboard component',
              ].map(suggestion => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setInput(suggestion);
                    inputRef.current?.focus();
                  }}
                  className="text-left px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm text-slate-600 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-4 max-w-3xl mx-auto">
          {messages.map(msg => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {/* Streaming message */}
          {streamingContent && (
            <div className="flex gap-3 animate-fade-in">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                <span className="text-sm">🤖</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-slate-100">
                  <div className="markdown-content text-sm text-slate-700">
                    <ReactMarkdown>{streamingContent}</ReactMarkdown>
                    <span className="inline-block w-2 h-4 bg-primary-500 animate-pulse ml-0.5" />
                  </div>
                </div>
                {streamingCitations.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {streamingCitations.map((c, i) => (
                      <span key={i} className="citation-badge" title={`${c.source}${c.guest ? ` - ${c.guest}` : ''}`}>
                        [Source {i + 1}] {c.source}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Loading indicator */}
          {isStreaming && !streamingContent && (
            <div className="flex gap-3 animate-fade-in">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                <span className="text-sm">🤖</span>
              </div>
              <div className="bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-slate-100">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Loader2 size={14} className="animate-spin" />
                  Thinking...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 border-t border-slate-200 bg-white">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="flex items-end gap-3 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus-within:border-primary-300 focus-within:ring-2 focus-within:ring-primary-100 transition-all">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about product management, growth strategies, or request artifacts..."
              className="flex-1 bg-transparent text-sm text-slate-700 placeholder-slate-400 resize-none focus:outline-none min-h-[24px] max-h-[200px]"
              rows={1}
              disabled={isStreaming}
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {isStreaming ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Send size={16} />
              )}
            </button>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">
            Responses are grounded in Lenny's Podcast transcripts. Press Enter to send, Shift+Enter for new line.
          </p>
        </form>
      </div>
    </div>
  );
}
