import { useState } from 'react'
import { api } from '../api'

export default function AdvisoryForm({ locations, crops, onSubmitSuccess, onCancel }) {
  const [locationName, setLocationName] = useState('')
  const [cropName, setCropName] = useState('')
  const [sowingDate, setSowingDate] = useState('')
  const [weatherObservation, setWeatherObservation] = useState('')
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

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!locationName) return setError('Please select a location.')
    if (!cropName) return setError('Please select a crop.')
    if (!sowingDate) return setError('Please select a sowing date.')
    if (new Date(sowingDate) > new Date()) {
      return setError('Sowing date cannot be in the future.')
    }

    setIsSubmitting(true)
    try {
      const payload = {
        location_name: locationName,
        crop_name: cropName,
        sowing_date: sowingDate,
        weather_observation: weatherObservation || null,
      }
      const result = await api.postAdvisory(payload)
      onSubmitSuccess(result, { locationName, cropName, sowingDate, weatherObservation, leafResult })
    } catch (err) {
      setError(err.message || 'Failed to submit advisory request. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-lg bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden transform transition duration-300 hover:shadow-2xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 px-6 py-5 text-white">
        <h2 className="text-xl font-bold tracking-tight">Get Precision Crop Advisory</h2>
        <p className="text-emerald-100 text-xs mt-1">
          Receive tailored irrigation, fertiliser, and pest management recommendations based on your local crop stage and weather.
        </p>
      </div>

      {/* Form Body */}
      <form onSubmit={handleSubmit} className="p-6 space-y-5">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-3 rounded text-sm font-medium animate-pulse">
            {error}
          </div>
        )}

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
            <option value="">-- Choose your location --</option>
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
            <option value="">-- Choose your crop --</option>
            {crops.map((c) => (
              <option key={c.id} value={c.name}>
                {c.name} ({c.category.replace('_', ' ')})
              </option>
            ))}
          </select>
        </div>

        {/* Sowing Date Picker */}
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
          <p className="text-xs text-slate-400 mt-1">Must be today or in the past.</p>
        </div>

        {/* Weather Observation Dropdown */}
        <div className="flex flex-col">
          <label htmlFor="weather-obs" className="text-sm font-semibold text-slate-700 mb-1.5">
            Field Weather Observation <span className="text-slate-400 font-normal">(Optional)</span>
          </label>
          <select
            id="weather-obs"
            value={weatherObservation}
            onChange={(e) => setWeatherObservation(e.target.value)}
            disabled={isSubmitting}
            className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition duration-200"
          >
            <option value="">Not sure (Skip / use forecast defaults)</option>
            <option value="hot_and_dry">Hot & Dry</option>
            <option value="humid_cloudy">Humid & Cloudy</option>
            <option value="light_rain">Light Rain</option>
            <option value="heavy_rain">Heavy Rain</option>
          </select>
        </div>

        {/* Photo Upload */}
        <div className="flex flex-col border border-dashed border-emerald-200 rounded-xl p-4 bg-emerald-50/70">
          <label className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
            Upload Leaf Image <span className="text-xs bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded font-normal uppercase tracking-wider">AI-Enhanced</span>
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
                Analyzing...
              </>
            ) : (
              'Generate Advisories'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
