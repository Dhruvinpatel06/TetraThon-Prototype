import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import AdvisoryForm from '../components/AdvisoryForm'

describe('AdvisoryForm Component', () => {
  const mockLocations = [{ id: 1, name: 'Anand', state: 'Gujarat' }]
  const mockCrops = [{ id: 1, name: 'Cotton', category: 'cash_crop' }]

  it('renders form fields and options correctly', () => {
    render(
      <AdvisoryForm
        locations={mockLocations}
        crops={mockCrops}
        onSubmitSuccess={vi.fn()}
        onCancel={vi.fn()}
      />
    )

    expect(screen.getByLabelText(/Select Location/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Select Crop/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Sowing Date/i)).toBeInTheDocument()
    expect(screen.getByText('Anand, Gujarat')).toBeInTheDocument()
    expect(screen.getByText(/Cotton/i)).toBeInTheDocument()
  })
})
