export function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_URL;
  if (typeof window !== 'undefined' && window.location) {
    const hostname = window.location.hostname;
    // Si se accede desde otra máquina en la red local (ej. 192.168.x.x) y VITE_API_URL
    // apunta a localhost o no está configurado, usar automáticamente el mismo host en puerto 8000
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      if (!envUrl || envUrl.includes('localhost') || envUrl.includes('127.0.0.1')) {
        return `${window.location.protocol}//${hostname}:8000`;
      }
    }
  }
  return (envUrl || 'http://localhost:8000').replace(/\/$/, '');
}

export const API_BASE_URL = getApiBaseUrl();

export function getTenantSubdomain() {
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'demo';
  }
  // Si se accede directamente por dirección IP (IPv4), no es un subdominio -> usar demo
  if (/^(\d{1,3}\.){3}\d{1,3}$/.test(host)) {
    return 'demo';
  }
  const parts = host.split('.');
  if (parts.length >= 3 && isNaN(parts[0])) {
    return parts[0].toLowerCase();
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
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}${cleanEndpoint}`;
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
