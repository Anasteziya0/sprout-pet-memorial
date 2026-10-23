const API_PREFIX = "/api/v1";
const ACCESS_TOKEN_KEY = "ecopet_token";
const REFRESH_TOKEN_KEY = "ecopet_refresh";

function getErrorMessage(data, fallback) {
  if (typeof data?.detail === "string") return data.detail;
  if (typeof data?.error === "string") return data.error;
  if (!data || typeof data !== "object") return fallback;

  const messages = Object.values(data).flatMap((value) =>
    Array.isArray(value) ? value : [value],
  ).filter((value) => typeof value === "string");
  return messages.join(" ") || fallback;
}

async function readResponse(response) {
  if (response.status === 204) return null;
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(getErrorMessage(data, `Ошибка запроса (${response.status})`));
  }
  if (response.headers.get("content-type")?.includes("application/pdf")) {
    return response.blob();
  }
  return response.json();
}

async function send(path, options, token) {
  const headers = new Headers(options.headers);
  let body = options.body;

  if (body != null && !(body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(body);
  }
  if (options.auth !== false && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return fetch(`${API_PREFIX}${path}`, {
    ...options,
    headers,
    body,
  });
}

export async function apiRequest(path, options = {}) {
  let accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  let response = await send(path, options, accessToken);

  if (response.status === 401 && options.auth !== false) {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refreshToken && !path.startsWith("/auth/")) {
      const refreshResponse = await send("/auth/refresh/", {
        method: "POST",
        body: { refresh: refreshToken },
        auth: false,
      });
      if (refreshResponse.ok) {
        const tokenData = await refreshResponse.json();
        accessToken = tokenData.access;
        localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
        response = await send(path, options, accessToken);
      } else {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
      }
    }
  }

  return readResponse(response);
}

export function saveTokens({ access, refresh }) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
