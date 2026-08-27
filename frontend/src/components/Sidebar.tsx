import { useState } from 'react';
import {
  MessageSquare, Plus, Trash2, ChevronLeft, ChevronRight,
  Pencil
} from 'lucide-react';
import { OpenAILogo, AnthropicLogo, OllamaLogo, OpenRouterLogo, LennyBrandLogo } from './ProviderLogos';
import type { Session, ModelInfo } from '../lib/types';

interface SidebarProps {
  sessions: Session[];
  activeSession: Session | null;
  onSelectSession: (session: Session) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  models: ModelInfo[];
  activeProvider: string;
  activeModel: string;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const PROVIDERS = [
  { id: 'ollama', label: 'Local', sublabel: 'Ollama', logo: OllamaLogo, badge: 'Zero Latency' },
  { id: 'openrouter', label: 'OpenRouter', sublabel: 'Multi-Model', logo: OpenRouterLogo, badge: null },
  { id: 'openai', label: 'OpenAI', sublabel: 'GPT Series', logo: OpenAILogo, badge: null },
  { id: 'anthropic', label: 'Claude', sublabel: 'Anthropic', logo: AnthropicLogo, badge: null },
];

function relativeTime(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  const diffD = Math.floor(diffH / 24);
  if (diffD === 1) return 'Yesterday';
  if (diffD < 7) return `${diffD}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function Sidebar({
  sessions, activeSession, onSelectSession, onNewChat, onDeleteSession,
  models, activeProvider, activeModel, onProviderChange, onModelChange,
  isOpen, onToggle,
}: SidebarProps) {
  const [hoveredSession, setHoveredSession] = useState<string | null>(null);
  const [showProviderSelect, setShowProviderSelect] = useState(false);

  const filteredModels = models.filter(m => {
    if (activeProvider === 'ollama') return m.is_local;
    return m.provider === activeProvider;
  });

  const currentProvider = PROVIDERS.find(p => p.id === activeProvider);

  return (
    <div
      className={`${isOpen ? 'w-72' : 'w-0'} transition-all duration-300 ease-out flex flex-col overflow-hidden relative`}
      style={{ background: 'linear-gradient(180deg, #0f172a 0%, #090d16 100%)' }}
    >
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-5 z-20 w-6 h-6 bg-surface-2 hover:bg-surface-3 border border-white/10 rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110"
      >
        {isOpen ? <ChevronLeft size={12} className="text-slate-400" /> : <ChevronRight size={12} className="text-slate-400" />}
      </button>

      {isOpen && (
        <div className="flex flex-col h-full relative z-10">
          {/* Brand Header */}
          <div className="px-5 pt-5 pb-4">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-indigo to-accent-violet flex items-center justify-center shadow-glow-sm overflow-hidden">
                  <LennyBrandLogo size={36} />
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-accent-emerald rounded-full border-2 border-surface-1 animate-pulse-dot" />
              </div>
              <div>
                <h1 className="text-sm font-bold text-white tracking-tight font-display">
                  Lenny Growth
                </h1>
                <p className="text-[10px] text-slate-500 font-medium tracking-wide uppercase">
                  PM & Growth Intelligence
                </p>
              </div>
            </div>
          </div>

          {/* New Chat Button */}
          <div className="px-3 pb-3">
            <button
              onClick={onNewChat}
              className="group w-full flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                bg-surface-2 hover:bg-surface-3 border border-white/[0.06] hover:border-white/[0.1]
                text-slate-300 hover:text-white"
            >
              <Plus size={16} className="transition-transform group-hover:rotate-90 duration-200" />
              <span>New Chat</span>
              <span className="ml-auto text-[10px] font-mono text-slate-500 bg-white/[0.04] px-1.5 py-0.5 rounded">
                ⌘K
              </span>
            </button>
          </div>

          {/* Model Selector */}
          <div className="px-3 pb-3">
            <label className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-2 block px-1">
              Model Provider
            </label>

            {/* Provider Grid */}
            <div className="grid grid-cols-2 gap-1.5 mb-2">
              {PROVIDERS.map(p => {
                const Logo = p.logo;
                const isActive = activeProvider === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => {
                      onProviderChange(p.id);
                      const firstModel = models.find(m => {
                        if (p.id === 'ollama') return m.is_local && m.is_available;
                        return m.provider === p.id && m.is_available;
                      });
                      if (firstModel) onModelChange(firstModel.model_id);
                    }}
                    className={`relative flex flex-col items-center gap-1 px-2 py-2 rounded-lg text-[11px] font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-accent-indigo/15 text-accent-indigo border border-accent-indigo/30 shadow-glow-sm'
                        : 'bg-white/[0.03] text-slate-500 border border-white/[0.04] hover:bg-white/[0.06] hover:text-slate-300'
                    }`}
                  >
                    <Logo size={15} />
                    <span>{p.label}</span>
                    {p.id === 'ollama' && isActive && (
                      <span className="absolute -top-1 -right-1 w-2 h-2 bg-accent-emerald rounded-full animate-pulse-dot" />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Model Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowProviderSelect(!showProviderSelect)}
                className="w-full flex items-center justify-between px-3 py-2 bg-white/[0.03] border border-white/[0.06] rounded-lg text-xs text-slate-400 hover:bg-white/[0.06] transition-all"
              >
                <span className="truncate text-slate-300">
                  {activeModel.split('/').pop() || activeModel}
                </span>
                <ChevronRight size={12} className={`transition-transform ${showProviderSelect ? 'rotate-90' : ''}`} />
              </button>

              {showProviderSelect && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-surface-2 border border-white/10 rounded-lg shadow-glass z-50 overflow-hidden">
                  {filteredModels.map(m => (
                    <button
                      key={m.model_id}
                      onClick={() => {
                        onModelChange(m.model_id);
                        setShowProviderSelect(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-xs transition-colors ${
                        activeModel === m.model_id
                          ? 'bg-accent-indigo/15 text-accent-indigo'
                          : 'text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="truncate">{m.display_name}</span>
                        {!m.is_available && (
                          <span className="text-[9px] text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">offline</span>
                        )}
                      </div>
                    </button>
                  ))}
                  {filteredModels.length === 0 && (
                    <p className="px-3 py-2 text-xs text-slate-600">No models available</p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Divider */}
          <div className="mx-4 h-px bg-white/[0.04]" />

          {/* Session List */}
          <div className="flex-1 overflow-y-auto px-3 py-3">
            <label className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-2 block px-1">
              Recent Chats
            </label>
            <div className="space-y-0.5">
              {sessions.map(session => {
                const isActive = activeSession?.id === session.id;
                const isHovered = hoveredSession === session.id;
                return (
                  <div
                    key={session.id}
                    className={`group relative flex items-center gap-2.5 px-3 py-2 rounded-lg cursor-pointer transition-all duration-150 ${
                      isActive
                        ? 'bg-white/[0.06] text-white'
                        : 'text-slate-400 hover:bg-white/[0.03] hover:text-slate-200'
                    }`}
                    onClick={() => onSelectSession(session)}
                    onMouseEnter={() => setHoveredSession(session.id)}
                    onMouseLeave={() => setHoveredSession(null)}
                  >
                    {/* Active indicator */}
                    {isActive && (
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-accent-indigo rounded-full" />
                    )}

                    <MessageSquare size={13} className="shrink-0 opacity-50" />
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] truncate leading-tight">{session.title}</p>
                      <p className="text-[10px] text-slate-600 mt-0.5">{relativeTime(session.updated_at)}</p>
                    </div>

                    {/* Hover Actions */}
                    {isHovered && (
                      <div className="flex items-center gap-0.5">
                        <button
                          onClick={(e) => { e.stopPropagation(); }}
                          className="p-1 text-slate-600 hover:text-slate-300 transition-colors rounded"
                        >
                          <Pencil size={11} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteSession(session.id);
                          }}
                          className="p-1 text-slate-600 hover:text-accent-rose transition-colors rounded"
                        >
                          <Trash2 size={11} />
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
              {sessions.length === 0 && (
                <div className="text-center py-8">
                  <div className="w-10 h-10 rounded-xl bg-white/[0.03] flex items-center justify-center mx-auto mb-2">
                    <MessageSquare size={16} className="text-slate-700" />
                  </div>
                  <p className="text-[11px] text-slate-600">No conversations yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Footer Status */}
          <div className="px-4 py-3 border-t border-white/[0.04]">
            <div className="flex items-center gap-2">
              <div className={`w-1.5 h-1.5 rounded-full ${
                activeProvider === 'ollama' ? 'bg-accent-emerald animate-pulse-dot' : 'bg-accent-indigo'
              }`} />
              <span className="text-[11px] text-slate-500">
                {currentProvider?.label || activeProvider}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
