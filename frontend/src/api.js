const configuredBase = import.meta.env.VITE_API_BASE_URL || "";
const API_BASE = configuredBase.replace(/\/$/, "");

export function getAccessToken() {
  return sessionStorage.getItem("inventory_access");
}

export function saveTokens(tokens) {
  sessionStorage.setItem("inventory_access", tokens.access);
  if (tokens.refresh) sessionStorage.setItem("inventory_refresh", tokens.refresh);
}

export function clearTokens() {
  sessionStorage.removeItem("inventory_access");
  sessionStorage.removeItem("inventory_refresh");
}

export async function apiRequest(path, options = {}) {
  const token = getAccessToken();
  const headers = new Headers(options.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearTokens();
    window.dispatchEvent(new Event("inventory:unauthorized"));
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const payload = await response.json();
      message = payload.detail || payload.message || Object.values(payload).flat().join(" ") || message;
    } catch {
      // Keep the HTTP status message when the response is not JSON.
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

export async function login(username, password) {
  const response = await fetch(`${API_BASE}/api/accounts/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Unable to sign in. Check your username and password.");
  saveTokens(data);
  return data;
}

export function listProducts() {
  return apiRequest("/api/products/?page_size=100");
}

export function listCategories() {
  return apiRequest("/api/products/categories/");
}

export function getMetrics() {
  return apiRequest("/api/products/dashboard/metrics/");
}
