import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from './lib/api';
import type { Session, Message, Citation, Artifact, ModelInfo } from './lib/types';
import Sidebar from './components/Sidebar';
import ChatView from './components/ChatView';
import ArtifactViewer from './components/ArtifactViewer';

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

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
    loadModels();
  }, []);

  // Load messages when session changes
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

  const handleSendMessage = useCallback(async (content: string) => {
    setError(null);
    
    // Add user message to UI immediately
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
              // Finalize the streaming message
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

  // Use refs to access latest state in callbacks
  const streamingContentRef = useRef(streamingContent);
  const streamingCitationsRef = useRef(streamingCitations);
  
  useEffect(() => {
    streamingContentRef.current = streamingContent;
  }, [streamingContent]);
  
  useEffect(() => {
    streamingCitationsRef.current = streamingCitations;
  }, [streamingCitations]);

  return (
    <div className="flex h-screen bg-slate-50">
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
      <div className="flex-1 flex flex-col min-w-0">
        {/* Error Toast */}
        {error && (
          <div className="absolute top-4 right-4 z-50 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg shadow-lg animate-fade-in">
            <div className="flex items-center gap-2">
              <span className="text-sm">{error}</span>
              <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
                ✕
              </button>
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
