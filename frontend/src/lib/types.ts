// ============================================================================
// Type definitions for the Lenny Growth Assistant frontend
// ============================================================================

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  llm_provider: string;
  model_name: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations: Citation[];
  has_artifact: string | null;
  artifact_id: string | null;
  created_at: string;
  token_count: number | null;
}

export interface Citation {
  source: string;
  guest: string | null;
  text_snippet: string;
  chunk_id: string | null;
  relevance_score: number | null;
}

export interface Artifact {
  id: string;
  session_id: string;
  artifact_type: 'html' | 'markdown';
  title: string;
  content: string;
  metadata: Record<string, any> | null;
  created_at: string;
}

export interface ModelInfo {
  provider: string;
  model_id: string;
  display_name: string;
  is_local: boolean;
  is_available: boolean;
}

export interface ChatRequest {
  session_id?: string | null;
  message: string;
  llm_provider?: string;
  model_name?: string;
  skill?: string | null;
}

export interface SSEEvent {
  type: 'session' | 'token' | 'citations' | 'artifact' | 'error' | 'done';
  data: any;
}

export type Skill = 'rag' | 'ship30' | 'artifact';
