import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE_URL });

function errorMessage(err) {
  return err?.response?.data?.detail || err.message || "Something went wrong.";
}

export const api = {
  baseUrl: API_BASE_URL,

  async health() {
    const { data } = await client.get("/api/health");
    return data;
  },

  async getProviders() {
    const { data } = await client.get("/api/providers");
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
