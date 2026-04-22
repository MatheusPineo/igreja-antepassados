import { Usuario, Antepassado } from "../types";

const API_URL = "http://localhost:8000";

export const api = {
  // Auth
  async login(data: any) {
    return this.post("/auth/login", data);
  },
  async register(data: any) {
    return this.post("/auth/register", data);
  },
  async googleAuth(credential: string) {
    return this.post("/auth/google", { credential });
  },

  // Antepassados
  async listAntepassados(usuarioId: number): Promise<Antepassado[]> {
    return this.get(`/antepassados/${usuarioId}`);
  },
  async createAntepassado(data: Antepassado): Promise<Antepassado> {
    return this.post("/antepassados/", data);
  },
  async deleteAntepassado(id: number) {
    return this.delete(`/antepassados/${id}`);
  },
  getExportUrl(usuarioId: number) {
    return `${API_URL}/antepassados/exportar-pdf/${usuarioId}`;
  },

  // Usuários
  async getUsuario(id: number): Promise<Usuario> {
    return this.get(`/usuarios/${id}`);
  },
  async updateUsuario(id: number, data: Partial<Usuario>): Promise<Usuario> {
    return this.put(`/usuarios/${id}`, data);
  },

  // Generic methods
  async post(endpoint: string, data: any) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  },
  async get(endpoint: string) {
    const response = await fetch(`${API_URL}${endpoint}`);
    return this.handleResponse(response);
  },
  async put(endpoint: string, data: any) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  },
  async delete(endpoint: string) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "DELETE",
    });
    return this.handleResponse(response);
  },
  async handleResponse(response: Response) {
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Erro na requisição");
    }
    return response.json();
  }
};
