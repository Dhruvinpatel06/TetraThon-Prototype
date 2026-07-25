import { describe, it, expect } from 'vitest'
import { formatCurrency, storageLabels } from '../utils'

describe('Frontend Utils', () => {
  it('formats currency correctly for INR', () => {
    expect(formatCurrency(1000)).toContain('1,000')
    expect(formatCurrency(0)).toContain('0.00')
    expect(formatCurrency(null)).toBe('₹0.00')
    expect(formatCurrency(undefined)).toBe('₹0.00')
  })

  it('maps storage labels correctly', () => {
    expect(storageLabels.open).toBe('Open Yard')
    expect(storageLabels.warehouse).toBe('Warehouse (Covered)')
    expect(storageLabels.cold_storage).toBe('Cold Storage')
  })
})
