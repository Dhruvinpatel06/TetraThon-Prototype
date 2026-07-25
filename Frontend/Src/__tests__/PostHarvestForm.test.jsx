import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import PostHarvestForm from '../components/PostHarvestForm'

describe('PostHarvestForm Component', () => {
  const mockLocations = [{ id: 1, name: 'Anand', state: 'Gujarat' }]
  const mockCrops = [{ id: 1, name: 'Cotton', category: 'cash_crop' }]

  it('renders form fields and storage options correctly', () => {
    render(
      <PostHarvestForm
        locations={mockLocations}
        crops={mockCrops}
        onSubmitSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    )

    expect(screen.getByLabelText(/Select Crop/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Quantity \(Quintals\)/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Storage Condition/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Select Location/i)).toBeInTheDocument()
    expect(screen.getByText('Warehouse (Covered)')).toBeInTheDocument()
  })
})
