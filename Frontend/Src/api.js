let API_BASE = import.meta.env.VITE_API_URL

if (!API_BASE) {
  if (import.meta.env.DEV) {
    console.warn("VITE_API_URL is missing. Silently falling back to http://localhost:8000 in development mode.")
    API_BASE = 'http://localhost:8000'
  } else {
    throw new Error("VITE_API_URL environment variable is required in production environment.")
  }
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(url, { ...options, signal: controller.signal })
    return res
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeoutMs / 1000}s`)
    }
    throw err
  } finally {
    clearTimeout(id)
  }
}

async function get(path, options = {}) {
  const res = await fetchWithTimeout(`${API_BASE}${path}`, options)
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `${path} failed: ${res.status}`)
  }
  return res.json()
}

async function post(path, body, options = {}) {
  const res = await fetchWithTimeout(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    ...options
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `${path} failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: (opts) => get('/api/health', opts),
  locations: (opts) => get('/api/locations', opts),
  crops: (opts) => get('/api/crops', opts),
  postAdvisory: (data, opts) => post('/api/advisory', data, opts),
  getRules: (cropName, opts) => get(`/api/rules?crop_name=${encodeURIComponent(cropName)}`, opts),
  postPostHarvest: (data, opts) => post('/api/post-harvest', data, opts),
  priceHistory: (crop, location, opts) => get(`/api/price-history?crop=${encodeURIComponent(crop || '')}&location=${encodeURIComponent(location || '')}`, opts),
  spoilageCurve: (crop, quantity, opts) => get(`/api/spoilage-curve?crop=${encodeURIComponent(crop || '')}&quantity=${encodeURIComponent(quantity || 10)}`, opts),
  postLeafClassify: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetchWithTimeout(`${API_BASE}/api/leaf-classify`, {
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