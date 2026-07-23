import { useState } from 'react'
import { api } from '../api'

export default function UnifiedScenarioForm({ locations, crops, onSubmitSuccess, onCancel }) {
  const [locationName, setLocationName] = useState('Ahmedabad')
  const [cropName, setCropName] = useState('Cotton')
  
  // Default sowing date to 45 days ago
  const defaultSowingDate = new Date(Date.now() - 45 * 86400000).toISOString().split('T')[0]
  const [sowingDate, setSowingDate] = useState(defaultSowingDate)
  const [weatherObservation, setWeatherObservation] = useState('')
  const [quantityQuintals, setQuantityQuintals] = useState('10.0')
  const [storageCondition, setStorageCondition] = useState('warehouse')

  const [leafPhoto, setLeafPhoto] = useState(null)
  const [leafResult, setLeafResult] = useState(null)
  const [isClassifying, setIsClassifying] = useState(false)

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const today = new Date().toISOString().split('T')[0]

  const handleLeafUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setLeafPhoto(file)
    setIsClassifying(true)
    setLeafResult(null)
    try {
      const result = await api.postLeafClassify(file)
      setLeafResult(result)
    } catch (err) {
      setLeafResult({ error: err.message || 'Classification failed' })
    } finally {
      setIsClassifying(false)
    }
  }

  const applyPreset = (preset) => {
    setError(null)
    const daysAgo = preset.daysAgo || 45
    const computedSowing = new Date(Date.now() - daysAgo * 86400000).toISOString().split('T')[0]
    
    setLocationName(preset.location)
    setCropName(preset.crop)
    setSowingDate(computedSowing)
    setWeatherObservation(preset.weather)
    setQuantityQuintals(preset.quantity.toString())
    setStorageCondition(preset.storage)
  }

  const presets = [
    {
      label: 'Cotton (Anand)',
      crop: 'Cotton',
      location: 'Anand',
      quantity: 10,
      storage: 'warehouse',
      daysAgo: 50,
      weather: 'hot_and_dry',
      badge: 'Dry Spell'
    },
    {
      label: 'Tomato (Surat)',
      crop: 'Tomato',
      location: 'Surat',
      quantity: 15,
      storage: 'open',
      daysAgo: 30,
      weather: 'humid_cloudy',
      badge: 'High Humidity'
    },
    {
      label: 'Wheat (Ahmedabad)',
      crop: 'Wheat',
      location: 'Ahmedabad',
      quantity: 25,
      storage: 'cold_storage',
      daysAgo: 75,
      weather: '',
      badge: 'Normal'
    },
    {
      label: 'Groundnut (Rajkot)',
      crop: 'Groundnut',
      location: 'Rajkot',
      quantity: 20,
      storage: 'warehouse',
      daysAgo: 60,
      weather: 'heavy_rain',
      badge: 'Heavy Rain'
    }
  ]

  const handleSubmit = async (e) => {
    if (e) e.preventDefault()
    setError(null)

    if (!locationName) return setError('Please select a location.')
    if (!cropName) return setError('Please select a crop.')
    if (!sowingDate) return setError('Please select a sowing date.')
    if (new Date(sowingDate) > new Date()) {
      return setError('Sowing date cannot be in the future.')
    }
    const qty = parseFloat(quantityQuintals)
    if (isNaN(qty) || qty <= 0) {
      return setError('Please enter a valid quantity greater than 0.')
    }
    if (!storageCondition) return setError('Please select a storage condition.')

    setIsSubmitting(true)

    try {
      const advisoryPayload = {
        location_name: locationName,
        crop_name: cropName,
        sowing_date: sowingDate,
        weather_observation: weatherObservation || null,
      }

      const postHarvestPayload = {
        crop_name: cropName,
        quantity_quintals: qty,
        storage_condition: storageCondition,
        location_name: locationName,
      }

      const [advisoryResult, postHarvestResult] = await Promise.all([
        api.postAdvisory(advisoryPayload),
        api.postPostHarvest(postHarvestPayload)
      ])

      onSubmitSuccess({
        inputs: {
          locationName,
          cropName,
          sowingDate,
          weatherObservation,
          quantityQuintals: qty,
          storageCondition,
          leafResult
        },
        advisory: advisoryResult,
        postHarvest: postHarvestResult,
        leafResult: leafResult
      })
    } catch (err) {
      setError(err.message || 'Failed to generate unified scenario recommendations.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-3xl bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden transform transition duration-300">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-700 via-teal-700 to-cyan-800 px-6 py-5 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
              Unified Intelligence Scenario Form
            </h2>
            <p className="text-emerald-100 text-xs mt-1">
              Analyze crop advisory (Module A) and post-harvest recommendations (Module B) simultaneously.
            </p>
          </div>
          <span className="hidden sm:inline-block bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-semibold">
            Phase 1 AI Engine
          </span>
        </div>
      </div>

      {/* Demo Presets Bar */}
      <div className="bg-slate-50 px-6 py-3 border-b border-slate-200">
        <p className="text-xs font-semibold text-slate-500 mb-2 flex items-center gap-1">
          Quick Evaluation Presets (One-Click Demo):
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {presets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPreset(p)}
              disabled={isSubmitting}
              className="text-left bg-white border border-slate-200 hover:border-emerald-500 p-2 rounded-xl text-xs shadow-sm hover:shadow transition duration-150 group"
            >
              <div className="font-bold text-slate-800 group-hover:text-emerald-700 truncate">{p.label}</div>
              <div className="text-[10px] text-slate-500 mt-0.5 flex justify-between items-center">
                <span>{p.quantity}q • {p.storage}</span>
                <span className="bg-emerald-50 text-emerald-700 font-medium px-1 rounded">{p.badge}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Form Body */}
      <form onSubmit={handleSubmit} className="p-6 space-y-5">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-3.5 rounded-xl text-sm font-medium animate-pulse">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Location Dropdown */}
          <div className="flex flex-col">
            <label htmlFor="location" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
              Select Location <span className="text-red-500">*</span>
            </label>
            <select
              id="location"
              value={locationName}
              onChange={(e) => setLocationName(e.target.value)}
              disabled={isSubmitting}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
            >
              <option value="">-- Choose location --</option>
              {locations.map((loc) => (
                <option key={loc.id} value={loc.name}>
                  {loc.name}, {loc.state}
                </option>
              ))}
            </select>
          </div>

          {/* Crop Dropdown */}
          <div className="flex flex-col">
            <label htmlFor="crop" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
              Select Crop <span className="text-red-500">*</span>
            </label>
            <select
              id="crop"
              value={cropName}
              onChange={(e) => setCropName(e.target.value)}
              disabled={isSubmitting}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
            >
              <option value="">-- Choose crop --</option>
              {crops.map((c) => (
                <option key={c.id} value={c.name}>
                  {c.name} ({c.category.replace('_', ' ')})
                </option>
              ))}
            </select>
          </div>

          {/* Sowing Date */}
          <div className="flex flex-col">
            <label htmlFor="sowing-date" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
              Sowing Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="sowing-date"
              value={sowingDate}
              max={today}
              onChange={(e) => setSowingDate(e.target.value)}
              disabled={isSubmitting}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
            />
          </div>

          {/* Weather Observation */}
          <div className="flex flex-col">
            <label htmlFor="weather-obs" className="text-sm font-semibold text-slate-700 mb-1.5">
              Weather Observation <span className="text-slate-400 font-normal">(Optional)</span>
            </label>
            <select
              id="weather-obs"
              value={weatherObservation}
              onChange={(e) => setWeatherObservation(e.target.value)}
              disabled={isSubmitting}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
            >
              <option value="">Normal (Forecast defaults)</option>
              <option value="hot_and_dry">Hot & Dry</option>
              <option value="humid_cloudy">Humid & Cloudy</option>
              <option value="light_rain">Light Rain</option>
              <option value="heavy_rain">Heavy Rain</option>
            </select>
          </div>

          {/* Quantity (Quintals) */}
          <div className="flex flex-col">
            <label htmlFor="quantity" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
              Produce Quantity (Quintals) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="quantity"
              min="0.5"
              step="0.5"
              max="1000"
              placeholder="e.g. 10.0"
              value={quantityQuintals}
              onChange={(e) => setQuantityQuintals(e.target.value)}
              disabled={isSubmitting}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
            />
          </div>

          {/* Storage Condition */}
          <div className="flex flex-col">
            <label htmlFor="storage-condition" className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1">
              Storage Condition <span className="text-red-500">*</span>
            </label>
            <select
              id="storage-condition"
              value={storageCondition}
              onChange={(e) => setStorageCondition(e.target.value)}
              disabled={isSubmitting}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
            >
              <option value="open">Open Yard</option>
              <option value="warehouse">Warehouse (Covered)</option>
              <option value="cold_storage">Cold Storage</option>
            </select>
          </div>

          {/* Photo Upload Field (Full Width) */}
          <div className="col-span-1 md:col-span-2 flex flex-col border border-dashed border-emerald-200 rounded-xl p-4 bg-emerald-50/70">
            <label className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              Upload Leaf Image <span className="text-xs bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded font-normal uppercase tracking-wider">Optional AI Analysis</span>
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleLeafUpload}
              disabled={isSubmitting || isClassifying}
              className="text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white file:cursor-pointer hover:file:bg-emerald-700"
            />
            {isClassifying && (
              <div className="flex items-center gap-2 mt-2 text-xs text-emerald-700 font-medium">
                <svg className="animate-spin h-3.5 w-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analyzing leaf image...
              </div>
            )}
            {leafResult && !leafResult.error && (
              <div className="mt-2.5 p-2.5 bg-white rounded-lg border border-emerald-100 shadow-sm">
                <p className="text-xs font-bold text-emerald-900 capitalize">
                  {leafResult.predicted_class.replace(/_/g, ' ')}
                  <span className="font-normal text-slate-500 ml-1.5">
                    ({Math.round(leafResult.confidence * 100)}% confidence)
                  </span>
                </p>
                {leafResult.is_healthy ? (
                  <p className="text-[11px] text-green-700 font-medium mt-0.5">Healthy crop - no disease symptoms detected</p>
                ) : (
                  <p className="text-[11px] text-amber-700 font-medium mt-0.5">Disease symptoms detected - consult local officer</p>
                )}
              </div>
            )}
            {leafResult?.error && (
              <p className="text-xs text-red-600 mt-2 font-medium">Classification failed: {leafResult.error}</p>
            )}
            <p className="text-xs text-slate-400 mt-1.5">AI-assisted analysis - not a certified diagnosis.</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-slate-100">
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="flex-1 px-4 py-2.5 border border-slate-200 text-slate-700 text-sm font-medium rounded-xl hover:bg-slate-50 transition duration-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-[2] bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white text-sm font-bold py-2.5 px-4 rounded-xl shadow-md transition duration-200 flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing Dual Intelligence Engines...
              </>
            ) : (
              'Evaluate Unified Scenario'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
