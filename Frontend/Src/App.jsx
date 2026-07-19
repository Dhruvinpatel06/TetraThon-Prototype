import { useEffect, useState } from 'react'
import { api } from './api'
import AdvisoryForm from './components/AdvisoryForm'
import AdvisoryResult from './components/AdvisoryResult'

export default function App() {
  const [health, setHealth] = useState(null)
  const [locations, setLocations] = useState([])
  const [crops, setCrops] = useState([])
  const [error, setError] = useState(null)
  
  // Navigation view state: 'home' | 'form' | 'results'
  const [view, setView] = useState('home')
  const [lastResult, setLastResult] = useState(null)
  const [inputs, setInputs] = useState(null)

  useEffect(() => {
    Promise.all([api.health(), api.locations(), api.crops()])
      .then(([h, loc, crp]) => {
        setHealth(h)
        setLocations(loc)
        setCrops(crp)
      })
      .catch((e) => setError(e.message))
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center py-10 px-4">
      {/* Title */}
      <div className="text-center max-w-2xl mb-8">
        <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight sm:text-4xl">
          Krishi Drishti
        </h1>
        <p className="text-slate-500 mt-2 font-medium">
          Precision Crop Advisory & Post-Harvest Decision Engine
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-xl text-sm font-medium max-w-2xl w-full mb-6">
          Could not reach backend: {error}
        </div>
      )}

      {/* Conditional View Rendering */}
      {view === 'home' && (
        <div className="flex flex-col items-center w-full max-w-2xl">
          {/* Main Action Button */}
          <div className="w-full bg-gradient-to-r from-emerald-600 to-teal-700 rounded-2xl shadow-lg p-6 text-white text-center mb-8 transform transition duration-300 hover:scale-[1.01]">
            <h2 className="text-xl font-bold">Need agronomy recommendations?</h2>
            <p className="text-emerald-100 text-sm mt-1 mb-4">
              Get stage-specific water, fertilizer, and pest advisories based on your local weather conditions.
            </p>
            <button
              onClick={() => setView('form')}
              className="inline-flex items-center justify-center bg-white text-emerald-800 font-bold px-6 py-3 rounded-xl shadow hover:bg-emerald-50 transition duration-200 gap-2"
            >
              <span>🌾</span> Get Crop Advisory
            </button>
          </div>

          {/* Health check card */}
          <div className="bg-white shadow border border-slate-100 rounded-2xl px-6 py-4 text-center mb-8 w-64">
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Backend health check</p>
            <p className="text-xl font-bold text-emerald-600 mt-1 flex items-center justify-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping inline-block" />
              {health ? health.status : 'checking...'}
            </p>
          </div>

          {/* Locations and Crops Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
            <div className="bg-white shadow border border-slate-100 rounded-2xl p-5 hover:shadow-md transition">
              <h2 className="font-bold text-slate-700 mb-3 flex items-center gap-1.5 text-base">
                📍 Deployed Locations ({locations.length})
              </h2>
              <ul className="text-slate-600 text-sm space-y-2">
                {locations.map((l) => (
                  <li key={l.id} className="flex justify-between py-1 border-b border-slate-100 last:border-b-0">
                    <span className="font-medium text-slate-800">{l.name}</span>
                    <span className="text-xs text-slate-400">{l.latitude.toFixed(2)}°, {l.longitude.toFixed(2)}°</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white shadow border border-slate-100 rounded-2xl p-5 hover:shadow-md transition">
              <h2 className="font-bold text-slate-700 mb-3 flex items-center gap-1.5 text-base">
                🌾 Configured Crops ({crops.length})
              </h2>
              <ul className="text-slate-600 text-sm space-y-2">
                {crops.map((c) => (
                  <li key={c.id} className="flex justify-between py-1 border-b border-slate-100 last:border-b-0">
                    <span className="font-medium text-slate-800">{c.name}</span>
                    <span className="text-xs text-slate-400">{c.typical_duration_days} days</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {view === 'form' && (
        <AdvisoryForm
          locations={locations}
          crops={crops}
          onSubmitSuccess={(res, inp) => {
            setLastResult(res)
            setInputs(inp)
            setView('results')
          }}
          onCancel={() => setView('home')}
        />
      )}

      {view === 'results' && (
        <AdvisoryResult
          result={lastResult}
          inputs={inputs}
          onNewAdvisory={() => setView('form')}
          onGoHome={() => setView('home')}
        />
      )}
    </div>
  )
}