import { useEffect, useState } from 'react'
import { api } from './api'
import AdvisoryForm from './components/AdvisoryForm'
import AdvisoryResult from './components/AdvisoryResult'
import PostHarvestForm from './components/PostHarvestForm'
import PostHarvestResult from './components/PostHarvestResult'
import Layout from './components/Layout'
import HealthCheck from './components/HealthCheck'
import LocationList from './components/LocationList'
import CropList from './components/CropList'

export default function App() {
  const [health, setHealth] = useState(null)
  const [locations, setLocations] = useState([])
  const [crops, setCrops] = useState([])
  const [error, setError] = useState(null)
  
  // Navigation view state: 'home' | 'form' | 'results' | 'ph-form' | 'ph-results'
  const [view, setView] = useState('home')
  const [lastResult, setLastResult] = useState(null)
  const [inputs, setInputs] = useState(null)

  // Post-Harvest States
  const [lastPHResult, setLastPHResult] = useState(null)
  const [phInputs, setPHInputs] = useState(null)

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
    <Layout>
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-xl text-sm font-medium max-w-2xl w-full mb-6">
          Could not reach backend: {error}
        </div>
      )}

      {/* Conditional View Rendering */}
      {view === 'home' && (
        <div className="flex flex-col items-center w-full max-w-2xl">
          {/* Main Action Buttons Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full mb-8">
            {/* Advisory Card */}
            <div className="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-2xl shadow-lg p-5 text-white flex flex-col justify-between transform transition duration-300 hover:scale-[1.01]">
              <div>
                <h3 className="text-lg font-bold">Crop Advisory</h3>
                <p className="text-emerald-100 text-xs mt-1 mb-4 leading-relaxed">
                  Get stage-specific water, fertilizer, and pest advisories based on local conditions.
                </p>
              </div>
              <button
                onClick={() => setView('form')}
                className="w-full inline-flex items-center justify-center bg-white text-emerald-800 font-bold py-2.5 px-4 rounded-xl shadow hover:bg-emerald-50 transition duration-200 gap-2 text-sm"
              >
                <span>🌾</span> Get Crop Advisory
              </button>
            </div>

            {/* Post-Harvest Card */}
            <div className="bg-gradient-to-br from-teal-700 to-cyan-800 rounded-2xl shadow-lg p-5 text-white flex flex-col justify-between transform transition duration-300 hover:scale-[1.01]">
              <div>
                <h3 className="text-lg font-bold">Post-Harvest Planner</h3>
                <p className="text-teal-100 text-xs mt-1 mb-4 leading-relaxed">
                  Optimize storage, transport, and selling timing to maximize net profits.
                </p>
              </div>
              <button
                onClick={() => setView('ph-form')}
                className="w-full inline-flex items-center justify-center bg-white text-teal-800 font-bold py-2.5 px-4 rounded-xl shadow hover:bg-teal-50 transition duration-200 gap-2 text-sm"
              >
                <span>📦</span> Plan Post-Harvest
              </button>
            </div>
          </div>

          {/* Health check card */}
          <HealthCheck health={health} />

          {/* Locations and Crops Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
            <LocationList locations={locations} />
            <CropList crops={crops} />
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

      {view === 'ph-form' && (
        <PostHarvestForm
          locations={locations}
          crops={crops}
          onSubmitSuccess={(res, inp) => {
            setLastPHResult(res)
            setPHInputs(inp)
            setView('ph-results')
          }}
          onCancel={() => setView('home')}
        />
      )}

      {view === 'ph-results' && (
        <PostHarvestResult
          result={lastPHResult}
          inputs={phInputs}
          onNewPlan={() => setView('ph-form')}
          onGoHome={() => setView('home')}
        />
      )}
    </Layout>
  )
}