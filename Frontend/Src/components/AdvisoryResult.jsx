import { useState } from 'react'
import LeafResult from './LeafResult'

export default function AdvisoryResult({ result, inputs, onNewAdvisory, onGoHome }) {
  const [expandedCard, setExpandedCard] = useState(null) // 'irrigation', 'fertiliser', 'pest', or null

  const toggleExpand = (type) => {
    setExpandedCard(expandedCard === type ? null : type)
  }

  const { locationName, cropName, sowingDate, weatherObservation, leafResult } = inputs
  const { advisories, session_id } = result

  // Weather observation display names
  const weatherLabels = {
    hot_and_dry: 'Hot & Dry',
    humid_cloudy: 'Humid & Cloudy',
    light_rain: 'Light Rain',
    heavy_rain: 'Heavy Rain',
  }

  // Icons for advisory types
  const getIcon = (type) => {
    switch (type) {
      case 'irrigation':
        return (
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-11.314l.707.707m11.314 11.314l.707-.707M12 5a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        )
      case 'fertiliser':
        return (
          <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        )
      case 'pest':
        return (
          <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      default:
        return null
    }
  }

  const getConfidenceBadge = (confidence) => {
    switch (confidence) {
      case 'High':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 border border-green-200">High Confidence</span>
      case 'Medium':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 border border-yellow-200">Medium Confidence</span>
      case 'Low':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 border border-red-200">Low Confidence</span>
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-100 text-slate-800">{confidence}</span>
    }
  }

  return (
    <div className="w-full max-w-xl bg-slate-50 rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 p-6 text-white text-center">
        <span className="text-xs font-semibold bg-emerald-800 bg-opacity-40 text-emerald-100 px-3 py-1 rounded-full uppercase tracking-wider">
          Session #{session_id} • Analysis Complete
        </span>
        <h2 className="text-2xl font-extrabold mt-3">Advisories for {cropName}</h2>
        <p className="text-emerald-100 text-sm mt-1">
          {locationName} • Sown on {new Date(sowingDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
        </p>
        {weatherObservation && (
          <p className="inline-block bg-teal-800 bg-opacity-40 text-teal-100 text-xs px-2.5 py-0.5 rounded-md mt-2 border border-teal-500 border-opacity-25">
            Field Obs: {weatherLabels[weatherObservation]}
          </p>
        )}
      </div>

      {/* Advisories List */}
      <div className="p-6 space-y-4">
        {/* Leaf Result Card (if uploaded) */}
        {leafResult && <LeafResult result={leafResult} />}

        {advisories.map((advisory) => {
          const isExpanded = expandedCard === advisory.type
          const details = advisory.details

          return (
            <div
              key={advisory.type}
              className={`bg-white rounded-xl border border-slate-200 overflow-hidden transition-all duration-300 ${
                isExpanded ? 'shadow-md border-emerald-500' : 'hover:shadow-md hover:border-slate-300'
              }`}
            >
              {/* Card Header (clickable to expand) */}
              <button
                onClick={() => toggleExpand(advisory.type)}
                className="w-full flex items-center justify-between p-4 focus:outline-none text-left"
              >
                <div className="flex items-center gap-3.5">
                  <div className="p-2 bg-slate-100 rounded-lg">{getIcon(advisory.type)}</div>
                  <div>
                    <h3 className="font-bold text-slate-800 text-base">{advisory.title}</h3>
                    <div className="mt-1">{getConfidenceBadge(advisory.confidence)}</div>
                  </div>
                </div>
                <div className="text-slate-400">
                  <svg
                    className={`w-5 h-5 transform transition-transform duration-300 ${
                      isExpanded ? 'rotate-180 text-emerald-600' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {/* Card Body - Plain Text */}
              <div className="px-4 pb-4 pt-1">
                <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 rounded-xl p-3.5 border border-slate-100 font-medium">
                  {advisory.plain_text}
                </p>
              </div>

              {/* Card Details (Expanded view) */}
              {isExpanded && details && (
                <div className="px-4 pb-4 border-t border-slate-100 bg-slate-50 bg-opacity-30 p-4 space-y-3.5 text-xs text-slate-600">
                  <h4 className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Technical Specifications</h4>
                  
                  {/* General Stage info */}
                  {details.stage && (
                    <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                      <span className="font-semibold text-slate-500">Crop Stage:</span>
                      <span className="font-bold text-slate-800">{details.stage}</span>
                    </div>
                  )}

                  {details.day_range && (
                    <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                      <span className="font-semibold text-slate-500">Active Days Range:</span>
                      <span className="font-medium text-slate-800">Day {details.day_range[0]} to {details.day_range[1]}</span>
                    </div>
                  )}

                  {/* Type Specific details */}
                  {advisory.type === 'irrigation' && (
                    <>
                      <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                        <span className="font-semibold text-slate-500">Water Depth:</span>
                        <span className="font-bold text-slate-800">{details.water_cm} cm</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                        <span className="font-semibold text-slate-500">Watering Frequency:</span>
                        <span className="font-bold text-slate-800">Every {details.interval_days} day(s)</span>
                      </div>
                      {details.skip_if_rain_expected && (
                        <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                          <span className="font-semibold text-slate-500">Rain Contingency:</span>
                          <span className="font-semibold text-blue-600">
                            Skip if rain in {details.skip_window_days} day(s)
                          </span>
                        </div>
                      )}
                    </>
                  )}

                  {advisory.type === 'fertiliser' && details.npk_kg_per_acre && (
                    <>
                      <div className="py-2 border-b border-slate-100">
                        <span className="font-semibold text-slate-500 block mb-1.5">N-P-K Recommendation per acre:</span>
                        <div className="flex gap-2">
                          <div className="flex-1 bg-emerald-50 text-emerald-800 text-center rounded-lg p-2 border border-emerald-100">
                            <div className="font-bold text-sm">{details.npk_kg_per_acre.N} kg</div>
                            <div className="text-[9px] uppercase tracking-wider text-emerald-600 font-semibold mt-0.5">Nitrogen (N)</div>
                          </div>
                          <div className="flex-1 bg-emerald-50 text-emerald-800 text-center rounded-lg p-2 border border-emerald-100">
                            <div className="font-bold text-sm">{details.npk_kg_per_acre.P} kg</div>
                            <div className="text-[9px] uppercase tracking-wider text-emerald-600 font-semibold mt-0.5">Phos (P)</div>
                          </div>
                          <div className="flex-1 bg-emerald-50 text-emerald-800 text-center rounded-lg p-2 border border-emerald-100">
                            <div className="font-bold text-sm">{details.npk_kg_per_acre.K} kg</div>
                            <div className="text-[9px] uppercase tracking-wider text-emerald-600 font-semibold mt-0.5">Potash (K)</div>
                          </div>
                        </div>
                      </div>
                      {details.note && (
                        <div className="py-1.5">
                          <span className="font-semibold text-slate-500">Agronomy Note:</span>
                          <p className="mt-1 text-slate-700 italic font-medium">"{details.note}"</p>
                        </div>
                      )}
                    </>
                  )}

                  {advisory.type === 'pest' && (
                    <>
                      <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                        <span className="font-semibold text-slate-500">Target Pest/Disease:</span>
                        <span className="font-bold text-amber-700">{details.pest_or_disease}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                        <span className="font-semibold text-slate-500">Base Stage Risk:</span>
                        <span className="font-medium text-slate-800">{details.default_risk}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 py-1.5 border-b border-slate-100">
                        <span className="font-semibold text-slate-500">Calculated Risk:</span>
                        <span className={`font-bold ${
                          details.calculated_risk === 'High' ? 'text-red-600' :
                          details.calculated_risk === 'Medium' ? 'text-amber-600' : 'text-green-600'
                        }`}>{details.calculated_risk}</span>
                      </div>
                      {details.raises_risk_if && details.raises_risk_if.length > 0 && (
                        <div className="py-1.5">
                          <span className="font-semibold text-slate-500">Risk Triggers:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {details.raises_risk_if.map((trigger) => (
                              <span key={trigger} className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded text-[10px] font-medium">
                                {trigger.replace('_', ' ')}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {details.is_generic_fallback && (
                    <div className="bg-amber-50 text-amber-800 p-2 rounded-lg border border-amber-200 text-[10px] flex items-center gap-1.5 mt-2">
                      <svg className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <span><strong>Notice:</strong> Sowing date exceeds typical duration. Showing generic end-of-stage rules.</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Footer Navigation Buttons */}
      <div className="bg-slate-100 border-t border-slate-200 p-4 flex gap-3">
        <button
          onClick={onGoHome}
          className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 text-sm font-semibold rounded-xl hover:bg-slate-50 transition duration-200"
        >
          Home Dashboard
        </button>
        <button
          onClick={onNewAdvisory}
          className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold py-2.5 px-4 rounded-xl shadow-md transition duration-200"
        >
          New Advisory
        </button>
      </div>
    </div>
  )
}
