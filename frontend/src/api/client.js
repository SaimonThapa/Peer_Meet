import { API_BASE_URL } from "@/lib/config";

export class AuthenticationError extends Error {}

let refreshPromise = null;
let onAuthFailure = null;

function readCookie(name) {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : "";
}

export function setAuthFailureHandler(handler) {
  onAuthFailure = handler;
}

async function parseResponse(response) {
  if (response.status === 204) return null;
  const text = await response.text();
  const body = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const message = body?.error?.message || "Request failed.";
    const error = new Error(message);
    error.status = response.status;
    error.code = body?.error?.code;
    throw error;
  }
  return body;
}

async function refreshAuth() {
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include"
    }).then(parseResponse).finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

export async function apiFetch(path, options = {}) {
  const skipRefresh = options.skipRefresh || path.includes("/auth/refresh") || path.includes("/auth/login") || path.includes("/auth/register");
  const method = (options.method || "GET").toUpperCase();
  const headers = { ...(options.headers || {}) };

  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrfToken = readCookie("csrf_token");
    if (csrfToken) headers["X-CSRF-Token"] = csrfToken;
  }

  const request = {
    ...options,
    credentials: "include",
    headers: options.body instanceof FormData ? headers : {
      "Content-Type": "application/json",
      ...headers
    }
  };
  delete request.skipRefresh;

  let response = await fetch(`${API_BASE_URL}${path}`, request);
  if (response.status === 401 && !skipRefresh) {
    try {
      await refreshAuth();
      response = await fetch(`${API_BASE_URL}${path}`, request);
    } catch {
      onAuthFailure?.();
      throw new AuthenticationError("Please sign in again.");
    }
    if (response.status === 401) {
      onAuthFailure?.();
      throw new AuthenticationError("Please sign in again.");
    }
  }
  return parseResponse(response);
}

export const jsonBody = (value) => JSON.stringify(value);
