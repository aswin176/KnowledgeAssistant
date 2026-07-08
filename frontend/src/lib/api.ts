import { getApiUrl, getToken } from "./utils";

export type GraphNode = {
  id: string;
  name?: string;
  _labels?: string[];
  [key: string]: unknown;
};

export type GraphRelationship = {
  type: string;
  start: string;
  end: string;
  properties?: Record<string, unknown>;
};

export type GraphResponse = {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
  center_id: string;
};

export type SearchResult = {
  id?: string;
  name?: string;
  _labels?: string[];
  score?: number;
  properties?: Record<string, unknown>;
};

export type SearchResponse = {
  results: SearchResult[];
  total: number;
  mode: string;
};

export type PersonListItem = {
  id: string;
  name: string;
  email?: string;
  current_employment?: string;
  [key: string]: unknown;
};

export type CompanyListItem = {
  id: string;
  name: string;
  industry?: string;
  [key: string]: unknown;
};

export type RelationshipSummary = {
  type?: string;
  node?: {
    name?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export type PersonDetail = {
  id: string;
  name: string;
  email?: string;
  mobile?: string;
  linkedin_url?: string;
  relationship_status?: string;
  current_employment?: string;
  current_city?: string;
  spouse_name?: string;
  kids?: number;
  bio?: string;
  relationships?: RelationshipSummary[];
  [key: string]: unknown;
};

export type CompanyDetail = {
  id: string;
  name: string;
  industry?: string;
  website?: string;
  description?: string;
  [key: string]: unknown;
};

export type ImportRecord = {
  id: string;
  filename: string;
  status: string;
  records_processed: number;
  records_created: number;
  records_merged: number;
  errors: string[];
  created_at?: string;
};

export type JobItem = {
  id: string;
  name: string;
  status: string;
  schedule?: string;
  last_run?: string;
  next_run?: string;
};

export type SettingsResponse = {
  llm_model: string;
  neo4j_connected: boolean;
  llm_available: boolean;
  supported_import_formats: string[];
};

export type HealthResponse = {
  status: string;
  neo4j: boolean;
  llm: boolean;
  version: string;
};

type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

type ChatHistoryItem = {
  role: string;
  content: string;
};

type ChatResponse = {
  answer: string;
  sources: Array<{ id?: string; name?: string; type?: string }>;
  conversation_id: string;
  cypher?: string | null;
  result_count: number;
};

type PersonListResponse = {
  items: PersonListItem[];
  total: number;
};

type CompanyListResponse = {
  items: CompanyListItem[];
  total: number;
};

type ImportListResponse = {
  items: ImportRecord[];
};

type JobListResponse = {
  items: JobItem[];
};

type RawSearchResult = {
  id?: string;
  name?: string;
  labels?: string[];
  _labels?: string[];
  score?: number;
  properties?: Record<string, unknown>;
};

export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${getApiUrl()}/api/v1`;
  }

  private headers(): Record<string, string> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  }

  private async readJson<T>(res: Response): Promise<T> {
    return (await res.json()) as T;
  }

  async login(username: string, password: string): Promise<LoginResponse> {
    const res = await fetch(`${this.baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error("Login failed");
    return this.readJson<LoginResponse>(res);
  }

  async chat(message: string, conversationId?: string, history?: ChatHistoryItem[]): Promise<ChatResponse> {
    const res = await fetch(`${this.baseUrl}/chat`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ message, conversation_id: conversationId, history }),
    });
    if (!res.ok) throw new Error("Chat request failed");
    return this.readJson<ChatResponse>(res);
  }

  async search(query: string, mode = "hybrid", limit = 20): Promise<SearchResponse> {
    const res = await fetch(`${this.baseUrl}/search`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ query, mode, limit }),
    });
    if (!res.ok) throw new Error("Search failed");
    const data = await this.readJson<{ results: RawSearchResult[]; total: number; mode: string }>(res);
    return {
      ...data,
      results: data.results.map((item) => ({
        ...item,
        _labels: item._labels ?? item.labels ?? [],
      })),
    };
  }

  async getPerson(id: string): Promise<PersonDetail> {
    const res = await fetch(`${this.baseUrl}/person/${id}`, { headers: this.headers() });
    if (!res.ok) throw new Error("Person not found");
    return this.readJson<PersonDetail>(res);
  }

  async listPersons(limit = 50, offset = 0): Promise<PersonListResponse> {
    const res = await fetch(`${this.baseUrl}/person?limit=${limit}&offset=${offset}`, {
      headers: this.headers(),
    });
    if (!res.ok) throw new Error("Failed to list persons");
    return this.readJson<PersonListResponse>(res);
  }

  async getCompany(id: string): Promise<CompanyDetail> {
    const res = await fetch(`${this.baseUrl}/company/${id}`, { headers: this.headers() });
    if (!res.ok) throw new Error("Company not found");
    return this.readJson<CompanyDetail>(res);
  }

  async listCompanies(limit = 50, offset = 0): Promise<CompanyListResponse> {
    const res = await fetch(`${this.baseUrl}/company?limit=${limit}&offset=${offset}`, {
      headers: this.headers(),
    });
    if (!res.ok) throw new Error("Failed to list companies");
    return this.readJson<CompanyListResponse>(res);
  }

  async exploreGraph(nodeId: string, depth = 2): Promise<GraphResponse> {
    const res = await fetch(`${this.baseUrl}/graph/explore`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ node_id: nodeId, depth }),
    });
    if (!res.ok) throw new Error("Graph explore failed");
    const data = await this.readJson<{
      nodes: GraphNode[];
      relationships: Array<{ type: string; start?: string; end?: string; properties?: Record<string, unknown> }>;
      center_id: string;
    }>(res);
    return {
      ...data,
      relationships: data.relationships.filter(
        (relationship): relationship is GraphRelationship =>
          typeof relationship.start === "string" && typeof relationship.end === "string"
      ),
    };
  }

  async uploadFile(file: File, merge = true): Promise<ImportRecord> {
    const formData = new FormData();
    formData.append("file", file);
    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${this.baseUrl}/upload?merge=${merge}`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return this.readJson<ImportRecord>(res);
  }

  async listImports(): Promise<ImportListResponse> {
    const res = await fetch(`${this.baseUrl}/import`, { headers: this.headers() });
    if (!res.ok) throw new Error("Failed to list imports");
    return this.readJson<ImportListResponse>(res);
  }

  async getJobs(): Promise<JobListResponse> {
    const res = await fetch(`${this.baseUrl}/jobs`, { headers: this.headers() });
    if (!res.ok) throw new Error("Failed to get jobs");
    return this.readJson<JobListResponse>(res);
  }

  async getSettings(): Promise<SettingsResponse> {
    const res = await fetch(`${this.baseUrl}/settings`, { headers: this.headers() });
    if (!res.ok) throw new Error("Failed to get settings");
    return this.readJson<SettingsResponse>(res);
  }

  async health(): Promise<HealthResponse> {
    const res = await fetch(`${this.baseUrl}/health`);
    return this.readJson<HealthResponse>(res);
  }

  createChatWebSocket(): WebSocket {
    const wsUrl = getApiUrl().replace("http", "ws");
    return new WebSocket(`${wsUrl}/api/v1/chat/ws`);
  }
}

export const api = new ApiClient();
