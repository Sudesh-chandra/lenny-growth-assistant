import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from './lib/api';
import type { Session, Message, Citation, Artifact, ModelInfo } from './lib/types';
import Sidebar from './components/Sidebar';
import ChatView from './components/ChatView';
import ArtifactViewer from './components/ArtifactViewer';
import { X, AlertCircle } from 'lucide-react';

export default function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [streamingCitations, setStreamingCitations] = useState<Citation[]>([]);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [activeProvider, setActiveProvider] = useState('openrouter');
  const [activeModel, setActiveModel] = useState('anthropic/claude-sonnet-4');
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [showArtifact, setShowArtifact] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    loadSessions();
    loadModels();
  }, []);

  useEffect(() => {
    if (activeSession) {
      loadMessages(activeSession.id);
    } else {
      setMessages([]);
    }
  }, [activeSession?.id]);

  const loadSessions = async () => {
    try {
      const data = await apiClient.listSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const loadModels = async () => {
    try {
      const data = await apiClient.getModels();
      setModels(data.models);
      setActiveProvider(data.active_provider);
      setActiveModel(data.active_model);
    } catch (err) {
      console.error('Failed to load models:', err);
    }
  };

  const loadMessages = async (sessionId: string) => {
    try {
      const data = await apiClient.getMessages(sessionId);
      setMessages(data);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleNewChat = useCallback(() => {
    setActiveSession(null);
    setMessages([]);
    setStreamingContent('');
    setStreamingCitations([]);
    setArtifact(null);
    setShowArtifact(false);
    setError(null);
  }, []);

  const handleSelectSession = useCallback((session: Session) => {
    setActiveSession(session);
    setStreamingContent('');
    setStreamingCitations([]);
    setArtifact(null);
    setShowArtifact(false);
    setError(null);
  }, []);

  const handleDeleteSession = useCallback(async (sessionId: string) => {
    try {
      await apiClient.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (activeSession?.id === sessionId) {
        handleNewChat();
      }
    } catch (err) {
      setError('Failed to delete session');
    }
  }, [activeSession, handleNewChat]);

  const handleOpenArtifact = useCallback(() => {
    setShowArtifact(true);
  }, []);

  const handleSendMessage = useCallback(async (content: string) => {
    setError(null);

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      session_id: activeSession?.id || '',
      role: 'user',
      content,
      citations: [],
      has_artifact: null,
      artifact_id: null,
      created_at: new Date().toISOString(),
      token_count: null,
    };
    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);
    setStreamingContent('');
    setStreamingCitations([]);

    try {
      await apiClient.chatStream(
        {
          session_id: activeSession?.id || null,
          message: content,
          llm_provider: activeProvider,
          model_name: activeModel,
        },
        (event) => {
          switch (event.type) {
            case 'session':
              if (!activeSession) {
                const newSession: Session = {
                  id: event.data.session_id,
                  title: content.slice(0, 50),
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                  llm_provider: activeProvider,
                  model_name: activeModel,
                };
                setActiveSession(newSession);
                setSessions(prev => [newSession, ...prev]);
              }
              break;
            case 'token':
              setStreamingContent(prev => prev + event.data);
              break;
            case 'citations':
              setStreamingCitations(event.data);
              break;
            case 'artifact':
              const newArtifact: Artifact = {
                id: `temp-artifact-${Date.now()}`,
                session_id: activeSession?.id || '',
                artifact_type: event.data.artifact_type,
                title: event.data.title,
                content: event.data.content,
                metadata: null,
                created_at: new Date().toISOString(),
              };
              setArtifact(newArtifact);
              setShowArtifact(true);
              break;
            case 'error':
              setError(event.data);
              break;
            case 'done':
              const assistantMessage: Message = {
                id: `msg-${Date.now()}`,
                session_id: activeSession?.id || '',
                role: 'assistant',
                content: streamingContentRef.current || '',
                citations: streamingCitationsRef.current || [],
                has_artifact: artifact ? artifact.artifact_type : null,
                artifact_id: artifact?.id || null,
                created_at: new Date().toISOString(),
                token_count: null,
              };
              setMessages(prev => [...prev, assistantMessage]);
              setStreamingContent('');
              setStreamingCitations([]);
              setIsStreaming(false);
              break;
          }
        },
        (err) => {
          setError(`Connection error: ${err.message}`);
          setIsStreaming(false);
        }
      );
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      setIsStreaming(false);
    }
  }, [activeSession, activeProvider, activeModel]);

  const streamingContentRef = useRef(streamingContent);
  const streamingCitationsRef = useRef(streamingCitations);

  useEffect(() => {
    streamingContentRef.current = streamingContent;
  }, [streamingContent]);

  useEffect(() => {
    streamingCitationsRef.current = streamingCitations;
  }, [streamingCitations]);

  return (
    <div className="flex h-screen bg-surface-0 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        models={models}
        activeProvider={activeProvider}
        activeModel={activeModel}
        onProviderChange={setActiveProvider}
        onModelChange={setActiveModel}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Error Toast */}
        {error && (
          <div className="absolute top-4 right-4 z-50 animate-fade-in">
            <div className="glass rounded-xl px-4 py-3 shadow-glass border border-accent-rose/20 max-w-sm">
              <div className="flex items-start gap-2.5">
                <AlertCircle size={16} className="text-accent-rose shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] text-slate-200">{error}</p>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Chat + Artifact split */}
        <div className="flex-1 flex min-h-0">
          {/* Chat View */}
          <div className={`flex-1 flex flex-col min-w-0 ${showArtifact ? 'max-w-[50%]' : ''}`}>
            <ChatView
              messages={messages}
              streamingContent={streamingContent}
              streamingCitations={streamingCitations}
              isStreaming={isStreaming}
              onSendMessage={handleSendMessage}
              sessionTitle={activeSession?.title || 'New Chat'}
              activeProvider={activeProvider}
              activeModel={activeModel}
              artifact={artifact}
              onOpenArtifact={handleOpenArtifact}
            />
          </div>

          {/* Artifact Viewer */}
          {showArtifact && artifact && (
            <ArtifactViewer
              artifact={artifact}
              onClose={() => setShowArtifact(false)}
            />
          )}
        </div>
      </div>
    </div>
  );
}
