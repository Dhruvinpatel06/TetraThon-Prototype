let API_BASE = import.meta.env.VITE_API_URL

if (!API_BASE) {
  if (import.meta.env.DEV) {
    console.warn("VITE_API_URL is missing. Silently falling back to http://localhost:8000 in development mode.")
    API_BASE = 'http://localhost:8000'
  } else {
    throw new Error("VITE_API_URL environment variable is required in production environment.")
  }
}

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
  priceHistory: (crop, location) => get(`/api/price-history?crop=${encodeURIComponent(crop || '')}&location=${encodeURIComponent(location || '')}`),
  spoilageCurve: (crop, quantity) => get(`/api/spoilage-curve?crop=${encodeURIComponent(crop || '')}&quantity=${encodeURIComponent(quantity || 10)}`),
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