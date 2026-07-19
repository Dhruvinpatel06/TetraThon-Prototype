const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`)
  return res.json()
}

export const api = {
  health: () => get('/health'),
  locations: () => get('/locations'),
  crops: () => get('/crops'),
}