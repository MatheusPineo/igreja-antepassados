import { Usuario, Antepassado } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "";

const getHeaders = () => {
  const token = localStorage.getItem("token");
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

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
  async listAntepassados(): Promise<Antepassado[]> {
    return this.get(`/antepassados/`);
  },
  async createAntepassado(data: Antepassado): Promise<Antepassado> {
    return this.post("/antepassados/", data);
  },
  async deleteAntepassado(id: number) {
    return this.delete(`/antepassados/${id}`);
  },
  getExportUrl() {
    return `${API_URL}/antepassados/exportar-pdf`;
  },

  // Usuários
  async getUsuario(): Promise<Usuario> {
    return this.get(`/usuarios/me`);
  },
  async updateUsuario(data: Partial<Usuario>): Promise<Usuario> {
    return this.put(`/usuarios/me`, data);
  },

  // Generic methods
  async post(endpoint: string, data: any) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  },
  async get(endpoint: string) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: getHeaders(),
    });
    return this.handleResponse(response);
  },
  async put(endpoint: string, data: any) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  },
  async delete(endpoint: string) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "DELETE",
      headers: getHeaders(),
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
