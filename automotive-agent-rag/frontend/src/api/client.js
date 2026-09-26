import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOKEN_STORAGE_KEY = "auth_token";

const client = axios.create({ baseURL: API_BASE_URL });

function errorMessage(err) {
  return err?.response?.data?.detail || err.message || "Something went wrong.";
}

let unauthorizedHandler = null;

export function onUnauthorized(handler) {
  unauthorizedHandler = handler;
}

export function setAuthToken(token) {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`;
    try {
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } catch {
      /* ignore */
    }
  } else {
    delete client.defaults.headers.common.Authorization;
    try {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    } catch {
      /* ignore */
    }
  }
}

export function getStoredToken() {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401 && unauthorizedHandler) {
      unauthorizedHandler();
    }
    return Promise.reject(error);
  }
);

export const api = {
  baseUrl: API_BASE_URL,

  async health() {
    const { data } = await client.get("/api/health");
    return data;
  },

  async register(email, password) {
    try {
      const { data } = await client.post("/api/auth/register", { email, password });
      return data;
    } catch (err) {
      throw new Error(errorMessage(err));
    }
  },

  async login(email, password) {
    try {
      const { data } = await client.post("/api/auth/login", { email, password });
      return data;
    } catch (err) {
      throw new Error(errorMessage(err));
    }
  },

  async logout() {
    try {
      await client.post("/api/auth/logout");
    } catch {
      /* logging out should never block the UI, even if the request fails */
    }
  },

  async me() {
    const { data } = await client.get("/api/auth/me");
    return data;
  },

  async getProviders() {
    const { data } = await client.get("/api/providers");
    return data;
  },

  async verifyProviders() {
    const { data } = await client.get("/api/providers/verify");
    return data;
  },

  async listManuals() {
    const { data } = await client.get("/api/manuals");
    return data;
  },

  async listPreloadedManuals() {
    const { data } = await client.get("/api/manuals/preloaded");
    return data;
  },

  async preloadManual(key) {
    try {
      const { data } = await client.post(`/api/manuals/preload/${key}`);
      return data;
    } catch (err) {
      throw new Error(errorMessage(err));
    }
  },

  async uploadManual({ file, brand, model, year }) {
    const form = new FormData();
    form.append("file", file);
    form.append("brand", brand);
    form.append("model", model);
    form.append("year", year);
    try {
      const { data } = await client.post("/api/manuals/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    } catch (err) {
      throw new Error(errorMessage(err));
    }
  },

  async resetManuals() {
    const { data } = await client.delete("/api/manuals");
    return data;
  },

  async chat({ message, provider, model, brand, vehicleModel, year }) {
    try {
      const { data } = await client.post("/api/chat", {
        message,
        provider,
        model,
        brand,
        vehicle_model: vehicleModel,
        year,
      });
      return data;
    } catch (err) {
      throw new Error(errorMessage(err));
    }
  },

  manualFileUrl(manualId) {
    return `${API_BASE_URL}/api/manuals/${manualId}/file`;
  },
};
