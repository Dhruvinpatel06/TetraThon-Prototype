const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`)
  return res.json()
}

async function post(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `${path} failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => get('/api/health'),
  locations: () => get('/api/locations'),
  crops: () => get('/api/crops'),
  postAdvisory: (data) => post('/api/advisory', data),
  getRules: (cropName) => get(`/api/rules?crop_name=${encodeURIComponent(cropName)}`),
  postPostHarvest: (data) => post('/api/post-harvest', data),
  postLeafClassify: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}/api/leaf-classify`, {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}))
      throw new Error(errorData.detail || `/api/leaf-classify failed: ${res.status}`)
    }
    return res.json()
  },
}