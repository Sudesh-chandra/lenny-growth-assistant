// ============================================================================
// API client for communicating with the FastAPI backend
// ============================================================================

import type { Session, Message, Artifact, ModelInfo, ChatRequest } from './types';

const API_BASE = '/api';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `API error: ${response.status}`);
    }
    return response.json();
  }

  // Health
  async health() {
    return this.fetch('/health');
  }

  // Models
  async getModels(): Promise<{ models: ModelInfo[]; active_provider: string; active_model: string }> {
    return this.fetch('/models');
  }

  // Sessions
  async createSession(title?: string, provider?: string, model?: string): Promise<Session> {
    return this.fetch('/sessions', {
      method: 'POST',
      body: JSON.stringify({ title, llm_provider: provider, model_name: model }),
    });
  }

  async listSessions(): Promise<Session[]> {
    return this.fetch('/sessions');
  }

  async getSession(sessionId: string): Promise<Session> {
    return this.fetch(`/sessions/${sessionId}`);
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.fetch(`/sessions/${sessionId}`, { method: 'DELETE' });
  }

  // Messages
  async getMessages(sessionId: string): Promise<Message[]> {
    return this.fetch(`/sessions/${sessionId}/messages`);
  }

  // Chat (non-streaming)
  async chat(request: ChatRequest) {
    return this.fetch('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Chat (streaming via SSE)
  async chatStream(
    request: ChatRequest,
    onEvent: (event: { type: string; data: any }) => void,
    onError?: (error: Error) => void,
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `Stream error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              onEvent(event);
            } catch {
              // Skip malformed events
            }
          }
        }
      }
    } catch (err) {
      if (onError) onError(err as Error);
    }
  }

  // Artifacts
  async getArtifact(artifactId: string): Promise<Artifact> {
    return this.fetch(`/artifacts/${artifactId}`);
  }
}

export const apiClient = new ApiClient();
