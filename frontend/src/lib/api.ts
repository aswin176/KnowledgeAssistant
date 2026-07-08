import { getApiUrl, getToken } from "./utils";

export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${getApiUrl()}/api/v1`;
  }

  private headers(): HeadersInit {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  }

  async login(username: string, password: string) {
    const res = await fetch(`${this.baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error("Login failed");
    return res.json();
  }

  async chat(message: string, conversationId?: string, history?: { role: string; content: string }[]) {
    const res = await fetch(`${this.baseUrl}/chat`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ message, conversation_id: conversationId, history }),
    });
    if (!res.ok) throw new Error("Chat request failed");
    return res.json();
  }

  async search(query: string, mode = "hybrid", limit = 20) {
    const res = await fetch(`${this.baseUrl}/search`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ query, mode, limit }),
    });
    if (!res.ok) throw new Error("Search failed");
    return res.json();
  }

  async getPerson(id: string) {
    const res = await fetch(`${this.baseUrl}/person/${id}`, { headers: this.headers() });
    if (!res.ok) throw new Error("Person not found");
    return res.json();
  }

  async listPersons(limit = 50, offset = 0) {
    const res = await fetch(`${this.baseUrl}/person?limit=${limit}&offset=${offset}`, {
      headers: this.headers(),
    });
    if (!res.ok) throw new Error("Failed to list persons");
    return res.json();
  }

  async getCompany(id: string) {
    const res = await fetch(`${this.baseUrl}/company/${id}`, { headers: this.headers() });
    if (!res.ok) throw new Error("Company not found");
    return res.json();
  }

  async listCompanies(limit = 50, offset = 0) {
    const res = await fetch(`${this.baseUrl}/company?limit=${limit}&offset=${offset}`, {
      headers: this.headers(),
    });
    if (!res.ok) throw new Error("Failed to list companies");
    return res.json();
  }

  async exploreGraph(nodeId: string, depth = 2) {
    const res = await fetch(`${this.baseUrl}/graph/explore`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ node_id: nodeId, depth }),
    });
    if (!res.ok) throw new Error("Graph explore failed");
    return res.json();
  }

  async uploadFile(file: File, merge = true) {
    const formData = new FormData();
    formData.append("file", file);
    const token = getToken();
    const headers: HeadersInit = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${this.baseUrl}/upload?merge=${merge}`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  }

  async listImports() {
    const res = await fetch(`${this.baseUrl}/import`, { headers: this.headers() });
    if (!res.ok) throw new Error("Failed to list imports");
    return res.json();
  }

  async getJobs() {
    const res = await fetch(`${this.baseUrl}/jobs`, { headers: this.headers() });
    if (!res.ok) throw new Error("Failed to get jobs");
    return res.json();
  }

  async getSettings() {
    const res = await fetch(`${this.baseUrl}/settings`, { headers: this.headers() });
    if (!res.ok) throw new Error("Failed to get settings");
    return res.json();
  }

  async health() {
    const res = await fetch(`${this.baseUrl}/health`);
    return res.json();
  }

  createChatWebSocket(): WebSocket {
    const wsUrl = getApiUrl().replace("http", "ws");
    return new WebSocket(`${wsUrl}/api/v1/chat/ws`);
  }
}

export const api = new ApiClient();
