export const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export function getTenantSubdomain() {
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'demo';
  }
  const parts = host.split('.');
  if (parts.length >= 3) {
    return parts[0];
  }
  return 'demo'; // fallback
}

export function getTenantHost() {
  if (typeof window !== 'undefined' && window.location) {
    return window.location.host;
  }
  return 'demo.printly.ar';
}

export function getApiUrl(endpoint) {
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  if (API_BASE_URL) {
    return `${API_BASE_URL}${cleanEndpoint}`;
  }
  return cleanEndpoint;
}

export async function apiFetch(url, options = {}) {
  const fullUrl = getApiUrl(url);
  const headers = new Headers(options.headers || {});

  headers.set('X-Tenant-Subdomain', getTenantSubdomain());

  const token = localStorage.getItem('token');
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  return fetch(fullUrl, {
    ...options,
    headers
  });
}
