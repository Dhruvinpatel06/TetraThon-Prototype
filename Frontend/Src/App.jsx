import { useEffect, useState } from 'react'
import { api } from './api'
import AdvisoryForm from './components/AdvisoryForm'
import AdvisoryResult from './components/AdvisoryResult'
import PostHarvestForm from './components/PostHarvestForm'
import PostHarvestResult from './components/PostHarvestResult'
import UnifiedScenarioForm from './components/UnifiedScenarioForm'
import Dashboard from './components/Dashboard'
import Layout from './components/Layout'
import HealthCheck from './components/HealthCheck'
import LocationList from './components/LocationList'
import CropList from './components/CropList'

export default function App() {
  const [health, setHealth] = useState(null)
  const [locations, setLocations] = useState([])
  const [crops, setCrops] = useState([])
  const [error, setError] = useState(null)
  
  // Navigation view state: 'home' | 'form' | 'results' | 'ph-form' | 'ph-results' | 'dashboard-form' | 'dashboard'
  const [view, setView] = useState('home')

  // Advisory Standalone States
  const [lastResult, setLastResult] = useState(null)
  const [inputs, setInputs] = useState(null)

  // Post-Harvest Standalone States
  const [lastPHResult, setLastPHResult] = useState(null)
  const [phInputs, setPHInputs] = useState(null)

  // Unified Dashboard States
  const [unifiedData, setUnifiedData] = useState(null)

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
    <Layout currentView={view} onNavigate={(targetView) => setView(targetView)}>
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-xl text-sm font-medium max-w-2xl w-full mb-6">
          Could not reach backend: {error}
        </div>
      )}

      {/* Conditional View Rendering */}
      {view === 'home' && (
        <div className="flex flex-col items-center w-full max-w-3xl">
          {/* Hero Banner */}
          <div className="w-full bg-gradient-to-r from-emerald-800 via-teal-800 to-cyan-900 rounded-3xl p-8 mb-8 text-white shadow-xl text-center sm:text-left relative overflow-hidden">
            <div className="relative z-10 max-w-xl">
              <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider">
                Precision AgriTech Solution
              </span>
              <h2 className="text-3xl font-extrabold mt-3 tracking-tight">
                AgriTech Platform
              </h2>
              <p className="text-emerald-100 text-sm mt-2 leading-relaxed font-medium">
                Dual-Engine Agricultural Decision Support System combining crop growth advisories with post-harvest loss minimization algorithms.
              </p>
              <div className="mt-6 flex flex-wrap gap-3 justify-center sm:justify-start">
                <button
                  onClick={() => setView('dashboard-form')}
                  className="bg-white text-emerald-950 font-extrabold text-sm py-3 px-6 rounded-xl shadow-lg hover:bg-emerald-50 transition duration-200 flex items-center gap-2"
                >
                  🚀 Open Unified Dashboard
                </button>
              </div>
            </div>
          </div>

          {/* Main Action Buttons Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 w-full mb-8">
            {/* Unified Dashboard Card */}
            <div className="bg-gradient-to-br from-slate-900 to-emerald-950 rounded-2xl shadow-lg p-5 text-white flex flex-col justify-between transform transition duration-300 hover:scale-[1.01] border border-emerald-800/40">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">
                  Combined View
                </span>
                <h3 className="text-lg font-bold mt-2">Unified Dashboard</h3>
                <p className="text-slate-300 text-xs mt-1 mb-4 leading-relaxed">
                  Evaluate crop stage advisory and market net return in a side-by-side dashboard with live charts.
                </p>
              </div>
              <button
                onClick={() => setView('dashboard-form')}
                className="w-full inline-flex items-center justify-center bg-emerald-500 text-slate-950 font-bold py-2.5 px-4 rounded-xl shadow hover:bg-emerald-400 transition duration-200 gap-2 text-xs"
              >
                📊 Open Dashboard
              </button>
            </div>

            {/* Advisory Card */}
            <div className="bg-gradient-to-br from-emerald-700 to-teal-800 rounded-2xl shadow-lg p-5 text-white flex flex-col justify-between transform transition duration-300 hover:scale-[1.01]">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-white/20 text-emerald-100 px-2 py-0.5 rounded">
                  Module A
                </span>
                <h3 className="text-lg font-bold mt-2">Crop Advisory</h3>
                <p className="text-emerald-100 text-xs mt-1 mb-4 leading-relaxed">
                  Get stage-specific water, fertilizer, and pest advisories based on local conditions.
                </p>
              </div>
              <button
                onClick={() => setView('form')}
                className="w-full inline-flex items-center justify-center bg-white text-emerald-900 font-bold py-2.5 px-4 rounded-xl shadow hover:bg-emerald-50 transition duration-200 gap-2 text-xs"
              >
                🌾 Crop Advisory
              </button>
            </div>

            {/* Post-Harvest Card */}
            <div className="bg-gradient-to-br from-teal-800 to-cyan-900 rounded-2xl shadow-lg p-5 text-white flex flex-col justify-between transform transition duration-300 hover:scale-[1.01]">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-white/20 text-teal-100 px-2 py-0.5 rounded">
                  Module B
                </span>
                <h3 className="text-lg font-bold mt-2">Post-Harvest Planner</h3>
                <p className="text-teal-100 text-xs mt-1 mb-4 leading-relaxed">
                  Optimize storage, transport, and selling timing to maximize net profits.
                </p>
              </div>
              <button
                onClick={() => setView('ph-form')}
                className="w-full inline-flex items-center justify-center bg-white text-teal-900 font-bold py-2.5 px-4 rounded-xl shadow hover:bg-teal-50 transition duration-200 gap-2 text-xs"
              >
                📦 Post-Harvest Plan
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

      {view === 'dashboard-form' && (
        <UnifiedScenarioForm
          locations={locations}
          crops={crops}
          onSubmitSuccess={(data) => {
            setUnifiedData(data)
            setView('dashboard')
          }}
          onCancel={() => setView('home')}
        />
      )}

      {view === 'dashboard' && unifiedData && (
        <Dashboard
          inputs={unifiedData.inputs}
          advisoryResult={unifiedData.advisory}
          postHarvestResult={unifiedData.postHarvest}
          onEditScenario={() => setView('dashboard-form')}
          onGoHome={() => setView('home')}
        />
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