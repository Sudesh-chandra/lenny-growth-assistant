import { MessageSquare, Plus, Trash2, ChevronLeft, ChevronRight, Cpu, Globe } from 'lucide-react';
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

export default function Sidebar({
  sessions,
  activeSession,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  models,
  activeProvider,
  activeModel,
  onProviderChange,
  onModelChange,
  isOpen,
  onToggle,
}: SidebarProps) {
  const localModels = models.filter(m => m.is_local);
  const cloudModels = models.filter(m => !m.is_local);

  return (
    <div
      className={`${
        isOpen ? 'w-72' : 'w-0'
      } transition-all duration-300 bg-slate-900 text-white flex flex-col overflow-hidden relative`}
    >
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-4 z-10 bg-slate-700 hover:bg-slate-600 rounded-full p-1 shadow-lg"
      >
        {isOpen ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
      </button>

      {isOpen && (
        <>
          {/* Header */}
          <div className="p-4 border-b border-slate-700">
            <h1 className="text-lg font-bold flex items-center gap-2">
              <span className="text-2xl">🚀</span>
              Lenny Growth Assistant
            </h1>
            <p className="text-xs text-slate-400 mt-1">PM & Growth Intelligence</p>
          </div>

          {/* New Chat Button */}
          <div className="p-3">
            <button
              onClick={onNewChat}
              className="w-full flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 rounded-lg text-sm font-medium transition-colors"
            >
              <Plus size={16} />
              New Chat
            </button>
          </div>

          {/* Model Selector */}
          <div className="px-3 pb-3">
            <label className="text-xs text-slate-400 uppercase tracking-wider mb-2 block">
              Model Provider
            </label>
            <div className="grid grid-cols-2 gap-1 mb-2">
              <button
                onClick={() => {
                  onProviderChange('ollama');
                  const firstLocal = localModels.find(m => m.is_available);
                  if (firstLocal) onModelChange(firstLocal.model_id);
                }}
                className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
                  activeProvider === 'ollama'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                <Cpu size={12} />
                Local
              </button>
              <button
                onClick={() => {
                  onProviderChange('openrouter');
                  const firstCloud = models.find(m => m.provider === 'openrouter' && m.is_available);
                  if (firstCloud) onModelChange(firstCloud.model_id);
                }}
                className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
                  activeProvider === 'openrouter'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                <Globe size={12} />
                OpenRouter
              </button>
              <button
                onClick={() => {
                  onProviderChange('openai');
                  const firstCloud = cloudModels.find(m => m.provider === 'openai' && m.is_available);
                  if (firstCloud) onModelChange(firstCloud.model_id);
                }}
                className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
                  activeProvider === 'openai'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                <Globe size={12} />
                OpenAI
              </button>
              <button
                onClick={() => {
                  onProviderChange('anthropic');
                  const firstCloud = cloudModels.find(m => m.provider === 'anthropic' && m.is_available);
                  if (firstCloud) onModelChange(firstCloud.model_id);
                }}
                className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
                  activeProvider === 'anthropic'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                <Globe size={12} />
                Claude
              </button>
            </div>
            
            {/* Model dropdown */}
            <select
              value={activeModel}
              onChange={(e) => onModelChange(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {models
                .filter(m => {
                  if (activeProvider === 'ollama') return m.is_local;
                  return m.provider === activeProvider;
                })
                .map(m => (
                  <option key={m.model_id} value={m.model_id}>
                    {m.display_name} {!m.is_available ? '(offline)' : ''}
                  </option>
                ))}
            </select>
          </div>

          {/* Session List */}
          <div className="flex-1 overflow-y-auto px-3 pb-3">
            <label className="text-xs text-slate-400 uppercase tracking-wider mb-2 block">
              Recent Chats
            </label>
            <div className="space-y-1">
              {sessions.map(session => (
                <div
                  key={session.id}
                  className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                    activeSession?.id === session.id
                      ? 'bg-slate-700 text-white'
                      : 'text-slate-300 hover:bg-slate-800'
                  }`}
                  onClick={() => onSelectSession(session)}
                >
                  <MessageSquare size={14} className="shrink-0" />
                  <span className="text-sm truncate flex-1">
                    {session.title}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-opacity"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
              {sessions.length === 0 && (
                <p className="text-xs text-slate-500 text-center py-4">
                  No conversations yet
                </p>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-slate-700">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <div className={`w-2 h-2 rounded-full ${
                activeProvider === 'ollama' ? 'bg-green-400' : 'bg-blue-400'
              }`} />
              <span>{
                activeProvider === 'ollama' ? 'Ollama Local' :
                activeProvider === 'openai' ? 'OpenAI Cloud' :
                activeProvider === 'anthropic' ? 'Anthropic Cloud' :
                activeProvider === 'openrouter' ? 'OpenRouter Cloud' :
                activeProvider
              }</span>
              <span className="ml-auto">{activeModel}</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
