const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || body.message || message;
    } catch {
      // Keep the HTTP status message.
    }
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  getVehicles: () => request("/vehicles"),
  getVehicle: (id) => request(`/vehicles/${encodeURIComponent(id)}`),
  getLatest: (id) => request(`/vehicles/${encodeURIComponent(id)}/latest`),
  getPrevious: (id) => request(`/vehicles/${encodeURIComponent(id)}/previous`),
  getHealth: (id) => request(`/vehicles/${encodeURIComponent(id)}/health`),
  getPrediction: (id) => request(`/vehicles/${encodeURIComponent(id)}/prediction`),
  getAgent: (id) => request(`/vehicles/${encodeURIComponent(id)}/agent`),
  trainModels: () => request("/models/train", { method: "POST" }),
  uploadCsv: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/upload-csv", { method: "POST", body: form });
  }
};