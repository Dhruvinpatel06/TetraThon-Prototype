import { useState } from 'react'
import { api } from '../api'

export default function PostHarvestForm({ locations, crops, onSubmitSuccess, onCancel }) {
  const [cropName, setCropName] = useState('')
  const [quantityQuintals, setQuantityQuintals] = useState('')
  const [storageCondition, setStorageCondition] = useState('')
  const [locationName, setLocationName] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!cropName) return setError('Please select a crop.')
    const qty = parseFloat(quantityQuintals)
    if (isNaN(qty) || qty <= 0) {
      return setError('Please enter a valid quantity greater than 0.')
    }
    if (!storageCondition) return setError('Please select a storage condition.')
    if (!locationName) return setError('Please select a location.')

    setIsSubmitting(true)
    try {
      const payload = {
        crop_name: cropName,
        quantity_quintals: qty,
        storage_condition: storageCondition,
        location_name: locationName,
      }
      const result = await api.postPostHarvest(payload)
      onSubmitSuccess(result, { cropName, quantityQuintals: qty, storageCondition, locationName })
    } catch (err) {
      setError(err.message || 'Failed to submit post-harvest request. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-lg bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden transform transition duration-300 hover:shadow-2xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 px-6 py-5 text-white">
        <h2 className="text-xl font-bold tracking-tight">📦 Plan Post-Harvest</h2>
        <p className="text-emerald-100 text-xs mt-1">
          Optimize your crop storage, transport, or selling decision based on market trends, transport costs, and spoilage estimates.
        </p>
      </div>

      {/* Form Body */}
      <form onSubmit={handleSubmit} className="p-6 space-y-5">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-3 rounded text-sm font-medium animate-pulse">
            {error}
          </div>
        )}

        {/* Crop Dropdown */}
        <div className="flex flex-col">
          <label htmlFor="crop" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
            🌾 Select Crop <span className="text-red-500">*</span>
          </label>
          <select
            id="crop"
            value={cropName}
            onChange={(e) => setCropName(e.target.value)}
            disabled={isSubmitting}
            className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
          >
            <option value="">-- Choose your crop --</option>
            {crops.map((c) => (
              <option key={c.id} value={c.name}>
                {c.name} ({c.category.replace('_', ' ')})
              </option>
            ))}
          </select>
        </div>

        {/* Quantity (Quintals) Input */}
        <div className="flex flex-col">
          <label htmlFor="quantity" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
            ⚖️ Quantity (Quintals) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="quantity"
            min="0.5"
            step="0.5"
            placeholder="e.g. 10.0"
            value={quantityQuintals}
            onChange={(e) => setQuantityQuintals(e.target.value)}
            disabled={isSubmitting}
            className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
          />
          <p className="text-xs text-slate-400 mt-1">1 Quintal = 100 kg. Must be greater than 0.</p>
        </div>

        {/* Storage Condition Dropdown */}
        <div className="flex flex-col">
          <label htmlFor="storage-condition" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
            🏢 Storage Condition <span className="text-red-500">*</span>
          </label>
          <select
            id="storage-condition"
            value={storageCondition}
            onChange={(e) => setStorageCondition(e.target.value)}
            disabled={isSubmitting}
            className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
          >
            <option value="">-- Select storage type --</option>
            <option value="open">Open Yard</option>
            <option value="warehouse">Warehouse (Covered)</option>
            <option value="cold_storage">Cold Storage</option>
          </select>
        </div>

        {/* Location Dropdown */}
        <div className="flex flex-col">
          <label htmlFor="location" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
            📍 Select Location <span className="text-red-500">*</span>
          </label>
          <select
            id="location"
            value={locationName}
            onChange={(e) => setLocationName(e.target.value)}
            disabled={isSubmitting}
            className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
          >
            <option value="">-- Choose your location --</option>
            {locations.map((loc) => (
              <option key={loc.id} value={loc.name}>
                {loc.name}, {loc.state}
              </option>
            ))}
          </select>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="flex-1 px-4 py-2.5 border border-slate-200 text-slate-700 text-sm font-medium rounded-xl hover:bg-slate-50 transition duration-200"
          >
            Back to Dashboard
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white text-sm font-bold py-2.5 px-4 rounded-xl shadow-md transition duration-200 flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Planning...
              </>
            ) : (
              'Plan Post-Harvest'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
