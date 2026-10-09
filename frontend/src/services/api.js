const configuredBase = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '');
const BASE = configuredBase || (import.meta.env.DEV ? 'http://localhost:5000' : '');

async function request(path, options = {}) {
  if (!BASE) {
    throw new Error('The API is not configured. Set VITE_API_BASE_URL for this deployment.');
  }
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Request failed.');
  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
};