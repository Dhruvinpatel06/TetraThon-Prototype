import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '../api'

describe('API Client', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches health status', async () => {
    const mockHealth = { status: 'OK', adapters: { weather: 'configured', prices: 'live' } }
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHealth
    })

    const res = await api.health()
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/health', expect.objectContaining({ signal: expect.any(Object) }))
    expect(res).toEqual(mockHealth)
  })

  it('fetches location list', async () => {
    const mockLocs = [{ id: 1, name: 'Anand', state: 'Gujarat' }]
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockLocs
    })

    const res = await api.locations()
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/locations', expect.objectContaining({ signal: expect.any(Object) }))
    expect(res).toEqual(mockLocs)
  })

  it('posts advisory request', async () => {
    const payload = { location_name: 'Anand', crop_name: 'Cotton', sowing_date: '2026-05-15' }
    const mockResult = { session_id: 1, advisories: [] }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResult
    })

    const res = await api.postAdvisory(payload)
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/advisory',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(payload)
      })
    )
    expect(res).toEqual(mockResult)
  })
})
