import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Zap, Code2, Target, Rocket, PenTool } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { LennyBrandLogo, LennyAvatar } from './ProviderLogos';
import type { Message, Citation, Artifact } from '../lib/types';
import MessageBubble from './MessageBubble';

interface ChatViewProps {
  messages: Message[];
  streamingContent: string;
  streamingCitations: Citation[];
  isStreaming: boolean;
  onSendMessage: (content: string) => void;
  sessionTitle: string;
  activeProvider: string;
  activeModel: string;
  artifact: Artifact | null;
  onOpenArtifact: () => void;
}

const STARTER_CARDS = [
  {
    icon: Rocket,
    category: 'Growth Strategy',
    color: 'from-accent-indigo/20 to-accent-violet/10',
    iconColor: 'text-accent-indigo',
    prompt: 'How do top startups build self-reinforcing growth loops?',
  },
  {
    icon: PenTool,
    category: 'Ship 30 for 30 Essay',
    color: 'from-accent-violet/20 to-accent-rose/10',
    iconColor: 'text-accent-violet',
    prompt: 'Write a 1,250-word deep dive on B2B SaaS pricing models.',
  },
  {
    icon: Code2,
    category: 'Interactive Tool',
    color: 'from-accent-emerald/20 to-accent-indigo/10',
    iconColor: 'text-accent-emerald',
    prompt: 'Build an interactive HTML/CSS ROI & LTV/CAC calculator widget.',
  },
  {
    icon: Target,
    category: 'PM Frameworks',
    color: 'from-accent-amber/20 to-accent-emerald/10',
    iconColor: 'text-accent-amber',
    prompt: 'How do Lenny\'s guests measure true Product-Market Fit?',
  },
];

export default function ChatView({
  messages, streamingContent, streamingCitations, isStreaming,
  onSendMessage, sessionTitle, activeProvider, activeModel, artifact, onOpenArtifact,
}: ChatViewProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const isEmpty = messages.length === 0 && !streamingContent;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

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

  const handleCardClick = (prompt: string) => {
    setInput(prompt);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const providerLabel = activeProvider === 'ollama' ? 'Local (Ollama)' :
    activeProvider === 'openai' ? 'OpenAI' :
    activeProvider === 'anthropic' ? 'Claude' :
    activeProvider === 'openrouter' ? 'OpenRouter' : activeProvider;

  return (
    <div className="flex flex-col h-full relative glow-bg">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto relative z-10">
        {isEmpty ? (
          /* ===== Welcome / Empty State ===== */
          <div className="flex flex-col items-center justify-center h-full px-6 text-center">
            {/* Ambient Glow */}
            <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-accent-indigo/[0.07] blur-3xl pointer-events-none" />

            <div className="relative animate-slide-up">
              {/* Greeting */}
              <h3 className="text-2xl font-bold text-white mb-2 font-display tracking-tight">
                What are we building or{' '}
                <span className="gradient-text">optimizing</span> today?
              </h3>
              <p className="text-sm text-slate-500 max-w-lg mx-auto mb-8 leading-relaxed">
                Ask product management and growth questions grounded in Lenny's Podcast transcripts.
                Generate content, essays, and interactive artifacts.
              </p>

              {/* Starter Cards */}
              <div className="grid grid-cols-2 gap-3 max-w-xl mx-auto">
                {STARTER_CARDS.map((card) => {
                  const Icon = card.icon;
                  return (
                    <button
                      key={card.category}
                      onClick={() => handleCardClick(card.prompt)}
                      className="starter-card text-left group"
                    >
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                        <Icon size={15} className={card.iconColor} />
                      </div>
                      <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                        {card.category}
                      </span>
                      <p className="text-[13px] text-slate-300 mt-1 leading-snug line-clamp-2 group-hover:text-white transition-colors">
                        {card.prompt}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          /* ===== Chat Messages ===== */
          <div className="px-6 py-6 max-w-3xl mx-auto">
            <div className="space-y-5">
              {messages.map(msg => (
                <MessageBubble
                  key={msg.id}
                  message={msg}
                  onOpenArtifact={msg.has_artifact ? onOpenArtifact : undefined}
                  artifactTitle={artifact?.title}
                />
              ))}

              {/* Streaming message */}
              {streamingContent && (
                <div className="flex gap-3 animate-fade-in">
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 overflow-hidden">
                    <LennyAvatar size={28} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="inline-block rounded-2xl rounded-tl-sm px-4 py-3 bg-white/[0.04] border border-white/[0.06] max-w-full">
                      <div className="markdown-content text-[13px] text-slate-300 leading-relaxed">
                        <ReactMarkdown>{streamingContent}</ReactMarkdown>
                        <span className="inline-block w-1.5 h-4 bg-accent-indigo rounded-full animate-pulse ml-0.5 align-text-bottom" />
                      </div>
                    </div>

                    {/* Streaming citations */}
                    {streamingCitations.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2.5">
                        {streamingCitations.map((c, i) => (
                          <span key={i} className="source-chip">
                            <span className="w-4 h-4 rounded-full bg-accent-indigo/20 flex items-center justify-center text-[9px] font-bold text-accent-indigo">
                              {i + 1}
                            </span>
                            <span className="truncate max-w-[120px]">{c.guest || c.source}</span>
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
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 overflow-hidden">
                    <LennyAvatar size={28} />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-white/[0.04] border border-white/[0.06]">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-accent-indigo" />
                        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-accent-indigo" />
                        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-accent-indigo" />
                      </div>
                      <span className="text-xs text-slate-500">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>

      {/* ===== Floating Bottom Input Bar ===== */}
      <div className="relative z-10 px-6 pb-5 pt-2">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit}>
            <div className="glass-input rounded-2xl shadow-glass transition-all focus-within:border-accent-indigo/30 focus-within:shadow-glow-sm">
              <div className="flex items-end gap-3 px-4 py-3">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about product management, growth strategies, or request artifacts..."
                  className="flex-1 bg-transparent text-sm text-slate-200 placeholder-slate-600 resize-none focus:outline-none min-h-[24px] max-h-[200px] leading-relaxed"
                  rows={1}
                  disabled={isStreaming}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isStreaming}
                  className="p-2.5 rounded-xl bg-gradient-to-r from-accent-indigo to-accent-violet text-white
                    hover:shadow-glow-sm disabled:opacity-30 disabled:cursor-not-allowed
                    transition-all duration-200 hover:-translate-y-0.5 disabled:hover:translate-y-0"
                >
                  {isStreaming ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Send size={16} />
                  )}
                </button>
              </div>
            </div>
          </form>
          <p className="text-[10px] text-slate-600 mt-2 text-center">
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
